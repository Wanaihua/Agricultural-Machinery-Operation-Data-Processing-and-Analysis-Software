import sqlite3
from pathlib import Path


def ensure_menu_in_db(db_path):
    p = Path(db_path)
    if not p.exists():
        print(f"DB not found: {db_path}")
        return

    conn = sqlite3.connect(str(p))
    cur = conn.cursor()

    # check menu table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menu';")
    if not cur.fetchone():
        print(f"No menu table in {db_path}")
        conn.close()
        return

    # check if track menu exists
    cur.execute("SELECT id FROM menu WHERE path=? OR page_path=?", ('/track', 'Track'))
    row = cur.fetchone()
    if row:
        menu_id = row[0]
        print(f"Menu '/track' already exists in {db_path} as id={menu_id}")
        cur.execute("UPDATE menu SET pid=? WHERE id=? AND IFNULL(pid, 0) <> 3", (3, menu_id))
        if cur.rowcount:
            conn.commit()
            print(f"Updated menu id={menu_id} pid=3 in {db_path}")
    else:
        cur.execute("SELECT MAX(id) FROM menu")
        mx = cur.fetchone()[0] or 0
        menu_id = mx + 1
        cur.execute(
            "INSERT INTO menu (id, name, path, icon, description, pid, page_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (menu_id, '轨迹管理', '/track', 'el-icon-location', '轨迹管理', 3, 'Track'),
        )
        conn.commit()
        print(f"Inserted '/track' into {db_path} as id={menu_id}")

    # ensure role_menu link for admin role
    cur.execute("SELECT id FROM role WHERE name=? OR flag=? LIMIT 1", ('admin', 'admin'))
    role_row = cur.fetchone()
    role_id = role_row[0] if role_row else None
    if not role_id:
        cur.execute("SELECT id FROM role LIMIT 1")
        r = cur.fetchone()
        role_id = r[0] if r else None

    if role_id:
        # check role_menu table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='role_menu';")
        if cur.fetchone():
            cur.execute("SELECT 1 FROM role_menu WHERE role_id=? AND menu_id=?", (role_id, menu_id))
            if not cur.fetchone():
                cur.execute("INSERT INTO role_menu (role_id, menu_id) VALUES (?, ?)", (role_id, menu_id))
                conn.commit()
                print(f"Linked role_id={role_id} to menu_id={menu_id} in {db_path}")
            else:
                print(f"role_menu already links role_id={role_id} and menu_id={menu_id} in {db_path}")
        else:
            print(f"No role_menu table in {db_path}")
    else:
        print(f"No role found in {db_path} to link menu")

    conn.close()


if __name__ == '__main__':
    # two DB locations used by the project
    root_db = Path(__file__).resolve().parents[2] / 'db.sqlite3'
    backend_db = Path(__file__).resolve().parents[1] / 'db.sqlite3'

    print('Ensuring /track menu in databases...')
    ensure_menu_in_db(root_db)
    ensure_menu_in_db(backend_db)
    print('Done')
