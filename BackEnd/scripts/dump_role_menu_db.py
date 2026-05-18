import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parents[1] / 'db.sqlite3'
conn = sqlite3.connect(str(db))
cur = conn.cursor()
cur.execute('SELECT role_id, menu_id FROM role_menu ORDER BY role_id, menu_id')
rows = cur.fetchall()
for r in rows:
    print(r)
conn.close()
