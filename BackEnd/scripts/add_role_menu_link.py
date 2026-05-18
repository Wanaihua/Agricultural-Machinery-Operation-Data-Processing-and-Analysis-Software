import sqlite3
from pathlib import Path

def add_link(db_path, role_id=1, menu_id=8):
    p = Path(db_path)
    if not p.exists():
        print('DB not found', db_path)
        return
    conn = sqlite3.connect(str(p))
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM role_menu WHERE role_id=? AND menu_id=?", (role_id, menu_id))
    if cur.fetchone():
        print('link exists in', db_path)
    else:
        try:
            cur.execute("INSERT INTO role_menu (role_id, menu_id) VALUES (?, ?)", (role_id, menu_id))
            conn.commit()
            print('inserted link into', db_path)
        except Exception as e:
            print('ERROR', e)
    conn.close()

if __name__ == '__main__':
    backend_db = Path(__file__).resolve().parents[1] / 'db.sqlite3'
    add_link(backend_db)
