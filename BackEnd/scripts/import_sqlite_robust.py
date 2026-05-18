import re
import sqlite3
from pathlib import Path
import sys


def normalize_sql(sql_text: str) -> str:
    s = sql_text
    s = re.sub(r"/\*!.*?\*/;", ";", s, flags=re.S)
    s = re.sub(r"/\*!.*?\*/", "", s, flags=re.S)
    s = s.replace('`', '"')
    s = re.sub(r"ENGINE=\w+\s*(DEFAULT CHARSET=[^\s;]+)?\s*(COLLATE=[^\s;]+)?", '', s, flags=re.IGNORECASE)
    s = re.sub(r"AUTO_INCREMENT=\d+", '', s, flags=re.IGNORECASE)
    s = re.sub(r"\bAUTO_INCREMENT\b", '', s, flags=re.IGNORECASE)
    s = re.sub(r"\bUNSIGNED\b", '', s, flags=re.IGNORECASE)
    s = re.sub(r"ROW_FORMAT=\w+", '', s, flags=re.IGNORECASE)
    # remove only the LOCK/UNLOCK and ALTER TABLE DISABLE/ENABLE KEYS lines, keep INSERTs inside
    s = re.sub(r"^\s*LOCK TABLES.*?$", "", s, flags=re.M|re.IGNORECASE)
    s = re.sub(r"^\s*UNLOCK TABLES.*?$", "", s, flags=re.M|re.IGNORECASE)
    s = re.sub(r"^\s*ALTER TABLE .*?DISABLE KEYS\s*;?\s*$", "", s, flags=re.M|re.IGNORECASE)
    s = re.sub(r"^\s*ALTER TABLE .*?ENABLE KEYS\s*;?\s*$", "", s, flags=re.M|re.IGNORECASE)
    s = re.sub(r"\bint\(\d+\)\b", "INTEGER", s, flags=re.IGNORECASE)
    s = re.sub(r"\bbigint\(\d+\)\b", "INTEGER", s, flags=re.IGNORECASE)
    s = re.sub(r"\bvarchar\(\d+\)\b", "TEXT", s, flags=re.IGNORECASE)
    s = re.sub(r"\bdouble\b", "REAL", s, flags=re.IGNORECASE)
    s = re.sub(r"\bfloat\b", "REAL", s, flags=re.IGNORECASE)
    s = re.sub(r"\bdecimal\(\d+,\s*\d+\)\b", "REAL", s, flags=re.IGNORECASE)
    s = re.sub(r"COMMENT\s+'[^']*'", "", s, flags=re.IGNORECASE)
    s = re.sub(r",\s*(UNIQUE\s+)?KEY\s+[^\(]*\([^\)]*\)", "", s, flags=re.IGNORECASE)
    s = re.sub(r",\s*INDEX\s+[^\(]*\([^\)]*\)", "", s, flags=re.IGNORECASE)
    s = re.sub(r",\s*CONSTRAINT\s+[^\(]*\([^\)]*\)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"REFERENCES\s+\"?[^\s\(\']+\"?\s*\([^\)]*\)\s*(ON DELETE [A-Z_]+)?\s*(ON UPDATE [A-Z_]+)?", "", s, flags=re.IGNORECASE)
    s = re.sub(r"ON UPDATE [A-Z_]+", "", s, flags=re.IGNORECASE)
    s = re.sub(r"ON DELETE [A-Z_]+", "", s, flags=re.IGNORECASE)
    s = re.sub(r",\s*\)", ")", s)
    # remove trailing DEFAULT CHARSET or other table-level options after closing )
    s = re.sub(r"\)\s*DEFAULT\s+CHARSET[^;]*;", ")", s, flags=re.IGNORECASE)
    s = re.sub(r"\)\s*DEFAULT\s+CHARSET[^;]*", ")", s, flags=re.IGNORECASE)
    # remove any stray double semicolons
    s = re.sub(r"\)\s*COMMENT\s*=\s*'[^']*'", ")", s, flags=re.IGNORECASE)
    s = re.sub(r";;+", ";", s)
    return s


def extract_statements(sql: str):
    # crude split by semicolon; keep CREATE/INSERT whole
    parts = [p.strip() for p in sql.split(';') if p.strip()]
    creates = []
    inserts = []
    others = []
    for p in parts:
        up = p.upper()
        if up.startswith('CREATE TABLE'):
            creates.append(p + ';')
        elif up.startswith('INSERT INTO') or up.startswith('REPLACE INTO'):
            inserts.append(p + ';')
        else:
            others.append(p + ';')
    return creates, inserts, others


def run(db_path: Path, dump_path: Path):
    if not dump_path.exists():
        print('Dump not found:', dump_path)
        return
    print('Using DB:', db_path)
    # create minimal required tables to accept inserts
    conn_p = sqlite3.connect(str(db_path))
    cur_p = conn_p.cursor()
    try:
        cur_p.executescript('''
        CREATE TABLE IF NOT EXISTS "user" ("id" INTEGER PRIMARY KEY, "username" TEXT, "password" TEXT);
        CREATE TABLE IF NOT EXISTS "role" ("id" INTEGER PRIMARY KEY, "name" TEXT);
        CREATE TABLE IF NOT EXISTS "menu" ("id" INTEGER PRIMARY KEY, "name" TEXT);
        CREATE TABLE IF NOT EXISTS "role_menu" ("id" INTEGER PRIMARY KEY, "role_id" INTEGER, "menu_id" INTEGER);
        CREATE TABLE IF NOT EXISTS "file" ("id" INTEGER PRIMARY KEY, "name" TEXT, "url" TEXT);
        CREATE TABLE IF NOT EXISTS "import_log" ("id" INTEGER PRIMARY KEY, "msg" TEXT);
        CREATE TABLE IF NOT EXISTS "dict" ("id" INTEGER PRIMARY KEY, "name" TEXT, "value" TEXT);
        CREATE TABLE IF NOT EXISTS "track" ("id" INTEGER PRIMARY KEY, "plot_no" TEXT);
        CREATE TABLE IF NOT EXISTS "trackpoints" ("id" INTEGER PRIMARY KEY, "track_id" INTEGER, "lat" REAL, "lng" REAL, "time" TEXT);
        ''')
        conn_p.commit()
    except Exception:
        pass
    cur_p.close()
    conn_p.close()
    sql = dump_path.read_text(encoding='utf-8', errors='ignore')
    sql = normalize_sql(sql)
    creates, inserts, others = extract_statements(sql)

    # ensure minimal user table exists to avoid CREATE incompatibilities
    conn_pre = sqlite3.connect(str(db_path))
    cur_pre = conn_pre.cursor()
    try:
        cur_pre.execute('''CREATE TABLE IF NOT EXISTS "user" (
            "id" INTEGER PRIMARY KEY,
            "username" TEXT,
            "password" TEXT,
            "nickname" TEXT,
            "email" TEXT,
            "phone" TEXT,
            "address" TEXT,
            "creat_time" TEXT,
            "avatar_url" TEXT,
            "role" TEXT
        );''')
        conn_pre.commit()
    except Exception:
        pass
    cur_pre.close()
    conn_pre.close()

    # prefer to create `user` table first if present
    creates_sorted = []
    user_create = [c for c in creates if re.search(r'CREATE\s+TABLE\s+"?user"?', c, flags=re.IGNORECASE)]
    if user_create:
        creates_sorted.extend(user_create)
    # then other creates
    for c in creates:
        if c not in user_create:
            creates_sorted.append(c)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    executed = 0
    failed = []

    print('Parsed statements: creates=', len(creates), 'inserts=', len(inserts), 'others=', len(others))

    # skip executing CREATE statements from dump (MySQL-specific syntax often incompatible)
    # for c in creates_sorted:
    #     try:
    #         cur.executescript(c)
    #         executed += 1
    #     except Exception as e:
    #         failed.append(('CREATE', c.replace('\n',' '), str(e)))

    def table_exists(cursor, name):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
        return cursor.fetchone() is not None

    def ensure_table_from_insert(cursor, insert_stmt):
        # try INSERT ... (col1,col2) VALUES ...
        m = re.match(r"INSERT\s+INTO\s+\"?([A-Za-z0-9_]+)\"?\s*\(([^\)]*)\)\s*VALUES", insert_stmt, flags=re.IGNORECASE)
        if m:
            tbl = m.group(1)
            cols = [c.strip().strip('"').strip() for c in m.group(2).split(',')]
            if table_exists(cursor, tbl):
                return
            cols_sql = ', '.join([f'"{c}" TEXT' for c in cols])
            sql = f'CREATE TABLE IF NOT EXISTS "{tbl}" ({cols_sql});'
            try:
                cursor.executescript(sql)
            except Exception as e:
                failed.append(('CREATE_FROM_INSERT', sql.replace('\n',' '), str(e)))
            return

        # fallback: INSERT INTO tbl VALUES (v1,v2,...)
        m2 = re.match(r"INSERT\s+INTO\s+\"?([A-Za-z0-9_]+)\"?\s*VALUES\s*\((.*?)\)", insert_stmt, flags=re.IGNORECASE|re.S)
        if not m2:
            return
        tbl = m2.group(1)
        first_tuple = m2.group(2)
        if table_exists(cursor, tbl):
            return
        # crude parse to count top-level commas (ignore commas inside single quotes)
        count = 0
        in_quote = False
        prev = ''
        for ch in first_tuple:
            if ch == "'" and prev != '\\':
                in_quote = not in_quote
            if ch == ',' and not in_quote:
                count += 1
            prev = ch
        num_fields = count + 1
        cols = [f'col{i+1}' for i in range(num_fields)]
        cols_sql = ', '.join([f'"{c}" TEXT' for c in cols])
        sql = f'CREATE TABLE IF NOT EXISTS "{tbl}" ({cols_sql});'
        try:
            cursor.executescript(sql)
        except Exception as e:
            failed.append(('CREATE_FROM_INSERT', sql.replace('\n',' '), str(e)))

    # execute other statements (like ALTER/SET) if any
    # but skip DROP TABLE statements to avoid removing pre-created minimal tables
    filtered_others = [o for o in others if not o.strip().upper().startswith('DROP TABLE')]
    for o in filtered_others:
        try:
            cur.executescript(o)
            executed += 1
        except Exception as e:
            failed.append(('OTHER', o.replace('\n',' '), str(e)))

    # insert priority: user first, then role, menu, role_menu, file, dict, import_log, track, trackpoints
    priority_tables = ['user', 'role', 'menu', 'role_menu', 'file', 'dict', 'import_log', 'machinery_track', 'track', 'trackpoints']
    def table_of_insert(stmt):
        m = re.match(r"INSERT\s+INTO\s+\"?([A-Za-z0-9_]+)\"?", stmt, flags=re.IGNORECASE)
        return m.group(1).lower() if m else ''

    inserts_by_table = {t: [] for t in priority_tables}
    other_inserts = []
    for ins in inserts:
        tbl = table_of_insert(ins)
        if tbl in inserts_by_table:
            inserts_by_table[tbl].append(ins)
        else:
            other_inserts.append(ins)

    # execute in priority order
    for t in priority_tables:
        for ins in inserts_by_table.get(t, []):
            try:
                ensure_table_from_insert(cur, ins)
                cur.executescript(ins)
                executed += 1
            except Exception as e:
                failed.append(('INSERT', ins.replace('\n',' '), str(e)))

    # execute remaining inserts
    for ins in other_inserts:
        try:
            ensure_table_from_insert(cur, ins)
            cur.executescript(ins)
            executed += 1
        except Exception as e:
            failed.append(('INSERT', ins.replace('\n',' '), str(e)))

    conn.commit()

    print(f'Executed {executed} statements; failures: {len(failed)}')
    for f in failed[:30]:
        print('--- FAILURE ---')
        print('TYPE:', f[0])
        print('ERR :', f[2])
        print('STMT:', f[1])
    # show counts
    key_tables = ['user', 'role', 'menu', 'role_menu', 'file', 'import_log', 'track', 'trackpoints', 'dict', 'machinery_track']
    for t in key_tables:
        try:
            cur.execute(f"SELECT COUNT(1) FROM {t}")
            print(t, cur.fetchone()[0])
        except Exception as e:
            print(t, 'ERR', e)

    # list tables
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print('Tables in DB:', tables)
    except Exception:
        pass

    cur.close()
    conn.close()


def main():
    root = Path(__file__).resolve().parents[2]
    dump = root / 'Dump20260518.sql'
    db = root / 'BackEnd' / 'db.sqlite3'
    run(db, dump)


if __name__ == '__main__':
    main()
