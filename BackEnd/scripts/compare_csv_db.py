from pathlib import Path
import csv
from datetime import datetime
import sqlite3

script_root = Path(__file__).resolve().parents[1]
project_root = Path(__file__).resolve().parents[2]
csv_dir = script_root / 'datasets' / 'csv'
db = project_root / 'db.sqlite3'

def parse_csv_bounds(path):
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        times = []
        count = 0
        for r in reader:
            if not r: continue
            t = None
            for fmt in ('%Y/%m/%d %H:%M', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
                try:
                    t = datetime.strptime(r[1].strip(), fmt)
                    break
                except Exception:
                    t = None
            if t is None:
                try:
                    t = datetime.fromisoformat(r[1].strip().replace('/', '-'))
                except Exception:
                    t = None
            if t:
                times.append(t)
            count += 1
    if not times:
        return None, None, count
    return min(times), max(times), count

def main():
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    print('Comparing CSV files with DB track rows:')
    for csvfile in sorted(csv_dir.glob('*.csv')):
        name = csvfile.stem
        if not name.isdigit():
            continue
        trackid = int(name)
        csv_start, csv_end, csv_count = parse_csv_bounds(csvfile)
        cur.execute('SELECT starttime,endtime,totalpoints FROM track WHERE trackid=?',(trackid,))
        row = cur.fetchone()
        db_start, db_end, db_count = (None,None,0)
        if row:
            db_start, db_end, db_count = row
        print('\nfile', csvfile.name)
        print(' csv -> start:', csv_start, ' end:', csv_end, ' count:', csv_count)
        print(' db  -> start:', db_start, ' end:', db_end, ' count:', db_count)
        if csv_count!= (db_count or 0) or (csv_start and str(csv_start)[:19] != (db_start or '') ):
            print('  => MISMATCH')
        else:
            print('  => OK')
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
