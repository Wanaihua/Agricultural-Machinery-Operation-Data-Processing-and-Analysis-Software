import sqlite3
from pathlib import Path


def set_pid(db_path, menu_id=8, pid=3):
    p = Path(db_path)
    if not p.exists():
        print('DB not found', db_path)
        return
    conn = sqlite3.connect(str(p))
    cur = conn.cursor()
    cur.execute("UPDATE menu SET pid=? WHERE id=?", (pid, menu_id))
    conn.commit()
    print(f'Updated menu {menu_id} pid={pid} in {db_path}')
    conn.close()


if __name__ == '__main__':
    root_db = Path(__file__).resolve().parents[2] / 'db.sqlite3'
    backend_db = Path(__file__).resolve().parents[1] / 'db.sqlite3'
    set_pid(root_db)
    set_pid(backend_db)
