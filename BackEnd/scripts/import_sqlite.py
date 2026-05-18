import re
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
# SQL dump is stored at workspace root
sql_file = Path(r'D:/PycharmProjects/Agricultural Machinery Operation Data Processing and Analysis Software/Dump20260421-1.sql')
db_file = BASE_DIR / 'db.sqlite3'

if not sql_file.exists():
    print('SQL dump not found:', sql_file)
    raise SystemExit(1)

sql_text = sql_file.read_text(encoding='utf-8', errors='ignore')
# Remove MySQL-specific statements
# Remove DELIMITER blocks
sql_text = re.sub(r"DELIMITER\s+\\w+", "", sql_text, flags=re.IGNORECASE)
# Remove /*! ... */ MySQL versioned comments
sql_text = re.sub(r"/\*!.*?\*/;", ";", sql_text, flags=re.S)
# Remove backticks
sql_text = sql_text.replace('`', '"')
# Remove ENGINE=..., DEFAULT CHARSET=..., COLLATE=...
sql_text = re.sub(r"ENGINE=\w+\s*(DEFAULT CHARSET=[^\s;]+)?\s*(COLLATE=[^\s;]+)?", "", sql_text, flags=re.IGNORECASE)
sql_text = re.sub(r"DEFAULT CHARSET=[^\s;]+", "", sql_text, flags=re.IGNORECASE)
sql_text = re.sub(r"COLLATE=[^\s;]+", "", sql_text, flags=re.IGNORECASE)
# Remove AUTO_INCREMENT=... in CREATE TABLE
sql_text = re.sub(r"AUTO_INCREMENT=\d+", "", sql_text, flags=re.IGNORECASE)
# Remove UNSIGNED keyword
sql_text = re.sub(r"\bUNSIGNED\b", "", sql_text, flags=re.IGNORECASE)
# Remove SET statements
sql_text = re.sub(r"^SET .*?;\n", "", sql_text, flags=re.MULTILINE)
# Remove LOCK/UNLOCK TABLES
sql_text = re.sub(r"LOCK TABLES .*?;", "", sql_text, flags=re.S)
sql_text = re.sub(r"UNLOCK TABLES;", "", sql_text, flags=re.IGNORECASE)
# Convert ENGINE/ROW_FORMAT like patterns to nothing
sql_text = re.sub(r"ROW_FORMAT=\w+", "", sql_text, flags=re.IGNORECASE)
# Remove /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */; etc
sql_text = re.sub(r"/\*!\d+ .*?\*/;", "", sql_text, flags=re.S)

# Split into statements by semicolon; careful with semicolons in strings
# Convert common MySQL types to SQLite equivalents
sql_text = re.sub(r"\bint\(\d+\)\b", "INTEGER", sql_text, flags=re.IGNORECASE)
sql_text = re.sub(r"\bbigint\(\d+\)\b", "INTEGER", sql_text, flags=re.IGNORECASE)
sql_text = re.sub(r"\bvarchar\(\d+\)\b", "TEXT", sql_text, flags=re.IGNORECASE)
sql_text = re.sub(r"\bdouble\b", "REAL", sql_text, flags=re.IGNORECASE)
sql_text = re.sub(r"\bfloat\b", "REAL", sql_text, flags=re.IGNORECASE)
# Convert decimal to REAL
sql_text = re.sub(r"\bdecimal\(\d+,\s*\d+\)\b", "REAL", sql_text, flags=re.IGNORECASE)
# Remove AUTO_INCREMENT occurrences
sql_text = re.sub(r"AUTO_INCREMENT", "", sql_text, flags=re.IGNORECASE)
# Remove column comments
sql_text = re.sub(r"COMMENT\s+'[^']*'", "", sql_text, flags=re.IGNORECASE)
# Remove MySQL KEY/INDEX declarations inside CREATE TABLE
sql_text = re.sub(r",\s*(UNIQUE\s+)?KEY\s+[^\(]*\([^\)]*\)", "", sql_text, flags=re.IGNORECASE)
# Remove simple INDEX clauses
sql_text = re.sub(r",\s*INDEX\s+[^\(]*\([^\)]*\)", "", sql_text, flags=re.IGNORECASE)
# Remove CONSTRAINT clauses
sql_text = re.sub(r",\s*CONSTRAINT\s+[^\(]*\([^\)]*\)", "", sql_text, flags=re.IGNORECASE)
# Remove REFERENCES/FOREIGN KEY clauses
sql_text = re.sub(r"REFERENCES\s+\"?[^\s\(\']+\"?\s*\([^\)]*\)\s*(ON DELETE [A-Z_]+)?\s*(ON UPDATE [A-Z_]+)?", "", sql_text, flags=re.IGNORECASE)
# Remove ON UPDATE / ON DELETE trailing clauses
sql_text = re.sub(r"ON UPDATE [A-Z_]+", "", sql_text, flags=re.IGNORECASE)
sql_text = re.sub(r"ON DELETE [A-Z_]+", "", sql_text, flags=re.IGNORECASE)
# Remove any trailing commas before closing parentheses
sql_text = re.sub(r",\s*\)", ")", sql_text)
# Remove table-level COMMENT clauses like ) COMMENT='...'
sql_text = re.sub(r"\)\s*COMMENT\s*=\s*'[^']*'", ")", sql_text, flags=re.IGNORECASE)
# Collapse multiple semicolons
sql_text = re.sub(r";\s*;",";", sql_text)
# Remove DEFAULT NULL (sqlite accepts NULL by default)
sql_text = re.sub(r"DEFAULT\s+NULL", "", sql_text, flags=re.IGNORECASE)
# Remove backslash-escaped newline sequences
sql_text = sql_text.replace('\\n', ' ')

stmts = [s.strip() + ';' for s in sql_text.split(';') if s.strip()]

print('Parsed', len(stmts), 'statements; executing into', db_file)
conn = sqlite3.connect(str(db_file))
cur = conn.cursor()
executed = 0
for s in stmts:
    try:
        cur.executescript(s)
        executed += 1
    except Exception as e:
        # print error and continue
        print('Failed statement preview:', s[:200].replace('\n',' '))
        print('Error:', e)
        # continue

conn.commit()
cur.close()
conn.close()
print('Executed', executed, 'statements')
