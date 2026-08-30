import csv
import sqlite3
from pathlib import Path
from datetime import datetime
import math


def haversine(lat1, lon1, lat2, lon2):
    # return distance in kilometers
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def parse_csv_file(path: Path):
    rows = []
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        for r in reader:
            if not r:
                continue
            # Expect: id, gpstime, lon, lat, x, y, speed, ???, workstatus(TRUE/FALSE), width, depth, depthstandard
            try:
                gpstime_raw = r[1].strip()
                # try multiple formats
                for fmt in ('%Y/%m/%d %H:%M', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
                    try:
                        gpstime = datetime.strptime(gpstime_raw, fmt)
                        break
                    except Exception:
                        gpstime = None
                if gpstime is None:
                    # fallback parse
                    gpstime = datetime.fromisoformat(gpstime_raw.replace('/', '-'))
                lon = float(r[2])
                lat = float(r[3])
            except Exception:
                continue

            speed = None
            try:
                speed = float(r[6])
            except Exception:
                speed = None

            workstatus = None
            try:
                ws = r[8].strip().upper()
                workstatus = 1 if ws in ('TRUE', '1', 'T') else 0
            except Exception:
                workstatus = None

            width = None
            try:
                width = float(r[9])
            except Exception:
                width = None

            rows.append({
                'gpstime': gpstime,
                'lon': lon,
                'lat': lat,
                'speed': speed,
                'workstatus': workstatus,
                'width': width,
            })

    # sort by gpstime
    rows.sort(key=lambda x: x['gpstime'] if x['gpstime'] else datetime.min)
    return rows


def import_all(datasets_dir: Path, db_path: Path):
    csv_dir = datasets_dir / 'csv'
    if not csv_dir.exists():
        print('csv dir not found:', csv_dir)
        return

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # ensure tables exist in expected schema
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS track (trackid INTEGER PRIMARY KEY, starttime TEXT, endtime TEXT, width REAL, totalpoints INTEGER);
    CREATE TABLE IF NOT EXISTS trackpoints (id INTEGER PRIMARY KEY AUTOINCREMENT, trackid INTEGER, gpstime TEXT, lon REAL, lat REAL, velocity REAL, workstatus INTEGER, width REAL);
    CREATE TABLE IF NOT EXISTS work (trackid INTEGER PRIMARY KEY, worktime REAL, worklength REAL, workarea REAL, avgvelocity REAL);
    CREATE TABLE IF NOT EXISTS rate (trackid INTEGER PRIMARY KEY, passrate REAL, productionrate REAL, timerrate REAL);
    ''')
    conn.commit()

    for csvfile in sorted(csv_dir.glob('*.csv')):
        name = csvfile.stem
        if not name.isdigit():
            continue
        trackid = int(name)
        print('\nProcessing', csvfile.name, 'as trackid', trackid)
        rows = parse_csv_file(csvfile)
        if not rows:
            print('  no rows parsed, skipping')
            continue

        # delete existing points for this track
        cur.execute('DELETE FROM trackpoints WHERE trackid=?', (trackid,))

        # insert points
        pts = []
        for r in rows:
            gpstime_s = r['gpstime'].strftime('%Y-%m-%d %H:%M:%S') if r['gpstime'] else None
            cur.execute('INSERT INTO trackpoints (trackid,gpstime,lon,lat,velocity,workstatus,width) VALUES (?,?,?,?,?,?,?)', (
                trackid, gpstime_s, r['lon'], r['lat'], r['speed'], r['workstatus'], r['width']
            ))
            pts.append((r['lat'], r['lon']))

        # compute stats
        start = rows[0]['gpstime']
        end = rows[-1]['gpstime']
        totalpoints = len(rows)
        # total distance (km)
        total_dist = 0.0
        for i in range(1, len(rows)):
            total_dist += haversine(rows[i-1]['lat'], rows[i-1]['lon'], rows[i]['lat'], rows[i]['lon'])

        speeds = [r['speed'] for r in rows if r['speed'] is not None]
        avg_speed = sum(speeds)/len(speeds) if speeds else 0.0

        worktime_hours = (end - start).total_seconds() / 3600.0 if start and end else 0.0

        avg_width = None
        widths = [r['width'] for r in rows if r['width'] is not None]
        if widths:
            avg_width = sum(widths)/len(widths)

        # approximate workarea (hectares) = total_dist(km) * avg_width(m) / 10
        workarea = None
        if avg_width is not None:
            workarea = total_dist * (avg_width / 1000.0) * 100  # in hectares (km * km => ha conversion)

        # upsert track
        cur.execute('REPLACE INTO track (trackid,starttime,endtime,width,totalpoints) VALUES (?,?,?,?,?)', (
            trackid,
            start.strftime('%Y-%m-%d %H:%M:%S') if start else None,
            end.strftime('%Y-%m-%d %H:%M:%S') if end else None,
            avg_width,
            totalpoints,
        ))

        # upsert work
        cur.execute('REPLACE INTO work (trackid,worktime,worklength,workarea,avgvelocity) VALUES (?,?,?,?,?)', (
            trackid, round(worktime_hours,3), round(total_dist,3), round(workarea,3) if workarea is not None else None, round(avg_speed,3)
        ))

        conn.commit()
        print(f'  imported {totalpoints} points, start={start}, end={end}, dist_km={total_dist:.3f}, avg_speed={avg_speed:.2f} km/h')

    cur.close()
    conn.close()


if __name__ == '__main__':
    script_root = Path(__file__).resolve().parents[1]
    project_root = Path(__file__).resolve().parents[2]
    datasets = script_root / 'datasets'
    db = project_root / 'db.sqlite3'
    print('datasets dir:', datasets)
    print('db path:', db)
    import_all(datasets, db)
