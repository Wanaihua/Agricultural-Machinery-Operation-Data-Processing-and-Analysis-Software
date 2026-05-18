import csv
import sqlite3
from pathlib import Path
from datetime import datetime


def parse_datetime(s: str):
    s = s.strip()
    for fmt in ('%Y/%m/%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S'):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


def import_all(db_path: Path, csv_dir: Path):
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    stats = {}
    for f in sorted(csv_dir.glob('*.csv')):
        name = f.stem
        rows = []
        with f.open('r', encoding='utf-8', errors='ignore') as fh:
            reader = csv.reader(fh)
            try:
                headers = next(reader)
            except StopIteration:
                continue
            for r in reader:
                if not r:
                    continue
                rows.append(r)

        if not rows:
            stats[name] = 0
            continue

        # parse times and numeric fields
        times = []
        points = []
        for i, r in enumerate(rows):
            # expect columns: index, GPS time, lon, lat, x, y, speed, course, workstatus, width, depth, depthstandard
            try:
                gpstime = parse_datetime(r[1]) if len(r) > 1 else None
                lon = float(r[2]) if len(r) > 2 and r[2] else None
                lat = float(r[3]) if len(r) > 3 and r[3] else None
                x = float(r[4]) if len(r) > 4 and r[4] else None
                y = float(r[5]) if len(r) > 5 and r[5] else None
                velocity = float(r[6]) if len(r) > 6 and r[6] else None
                course = float(r[7]) if len(r) > 7 and r[7] else None
                workstatus = 1 if (len(r) > 8 and (r[8].strip().upper() in ('TRUE','1','T')) ) else 0
                width = float(r[9]) if len(r) > 9 and r[9] else None
                depth = int(r[10]) if len(r) > 10 and r[10] else None
                depthstandard = int(r[11]) if len(r) > 11 and r[11] else None
            except Exception:
                gpstime = None
                lon = lat = x = y = velocity = course = None
                workstatus = 0
                width = depth = depthstandard = None

            if gpstime:
                times.append(gpstime)
            points.append((i+1, gpstime, lon, lat, x, y, velocity, course, workstatus, width, depth, depthstandard))

        start = times[0].isoformat(sep=' ') if times else None
        end = times[-1].isoformat(sep=' ') if times else None
        total = len(points)

        # insert track
        cur.execute('INSERT INTO track (starttime, endtime, width, totalpoints) VALUES (?,?,?,?)', (start, end, None, total))
        trackid = cur.lastrowid

        # insert trackpoints
        for seq, gpstime, lon, lat, x, y, velocity, course, workstatus, w, depth, depthstandard in points:
            cur.execute('INSERT INTO trackpoints (trackid, id, gpstime, lon, lat, x, y, velocity, course, workstatus, width, depth, depthstandard) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', (
                trackid, seq, gpstime.isoformat(sep=' ') if gpstime else None, lon, lat, x, y, velocity, course, workstatus, w, depth, depthstandard
            ))

        conn.commit()
        stats[name] = total

    cur.close()
    conn.close()
    return stats


def main():
    root = Path(__file__).resolve().parents[2]
    db = root / 'BackEnd' / 'db.sqlite3'
    csv_dir = root / 'BackEnd' / 'datasets' / 'csv'
    stats = import_all(db, csv_dir)
    print('Imported tracks from CSV:', stats)


if __name__ == '__main__':
    main()
