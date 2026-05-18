import re
from pathlib import Path
p=Path(r'D:/PycharmProjects/Agricultural Machinery Operation Data Processing and Analysis Software/Dump20260421-1.sql')
s=p.read_text(encoding='utf-8',errors='ignore')
# apply same cleaning
s=re.sub(r"DELIMITER\s+\\w+", "", s, flags=re.IGNORECASE)
s=re.sub(r"/\*!.*?\*/;", ";", s, flags=re.S)
s=s.replace('`','"')
s=re.sub(r"ENGINE=\w+\s*(DEFAULT CHARSET=[^\s;]+)?\s*(COLLATE=[^\s;]+)?", "", s, flags=re.IGNORECASE)
s=re.sub(r"DEFAULT CHARSET=[^\s;]+", "", s, flags=re.IGNORECASE)
s=re.sub(r"COLLATE=[^\s;]+", "", s, flags=re.IGNORECASE)
s=re.sub(r"AUTO_INCREMENT=\d+", "", s, flags=re.IGNORECASE)
s=re.sub(r"\bUNSIGNED\b","",s,flags=re.IGNORECASE)
s=re.sub(r"^SET .*?;\n","",s,flags=re.MULTILINE)
s=re.sub(r"LOCK TABLES .*?;","",s,flags=re.S)
s=re.sub(r"UNLOCK TABLES;","",s,flags=re.IGNORECASE)
s=re.sub(r"ROW_FORMAT=\w+","",s,flags=re.IGNORECASE)
s=re.sub(r"/\*!\d+ .*?\*/;","",s,flags=re.S)
s=re.sub(r"\bint\(\d+\)\b","INTEGER",s,flags=re.IGNORECASE)
s=re.sub(r"\bbigint\(\d+\)\b","INTEGER",s,flags=re.IGNORECASE)
s=re.sub(r"\bvarchar\(\d+\)\b","TEXT",s,flags=re.IGNORECASE)
s=re.sub(r"\bdouble\b","REAL",s,flags=re.IGNORECASE)
s=re.sub(r"\bfloat\b","REAL",s,flags=re.IGNORECASE)
s=re.sub(r"\bdecimal\(\d+,\s*\d+\)\b","REAL",s,flags=re.IGNORECASE)
s=re.sub(r"AUTO_INCREMENT","",s,flags=re.IGNORECASE)
s=re.sub(r"COMMENT\s+'[^']*'","",s,flags=re.IGNORECASE)
s=re.sub(r",\s*(UNIQUE\s+)?KEY\s+[^\(]*\([^\)]*\)","",s,flags=re.IGNORECASE)
s=re.sub(r",\s*INDEX\s+[^\(]*\([^\)]*\)","",s,flags=re.IGNORECASE)
s=re.sub(r",\s*CONSTRAINT\s+[^\(]*\([^\)]*\)","",s,flags=re.IGNORECASE)
s=re.sub(r"REFERENCES\s+\"?[^\s\(\']+\"?\s*\([^\)]*\)\s*(ON DELETE [A-Z_]+)?\s*(ON UPDATE [A-Z_]+)?","",s,flags=re.IGNORECASE)
s=re.sub(r"ON UPDATE [A-Z_]+","",s,flags=re.IGNORECASE)
s=re.sub(r"ON DELETE [A-Z_]+","",s,flags=re.IGNORECASE)
s=re.sub(r",\s*\)",")",s)

# find CREATE TABLE import_log and machinery_track blocks
for name in ['import_log','machinery_track']:
    m=re.search(rf'CREATE TABLE "{name}"\s*\((.*?)\)\s*;',s,flags=re.S|re.I)
    if m:
        block=m.group(0)
        print('---',name,'---')
        print(block)
    else:
        print(name,'not found')

# also print nearby lines in original
print('\n---- original snippet for import_log ----')
orig=p.read_text(encoding='utf-8',errors='ignore')
start=orig.find('CREATE TABLE `import_log`')
print(orig[start:start+400])
