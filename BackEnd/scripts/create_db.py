import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='wanaihua', port=3306)
cur = conn.cursor()
cur.execute("CREATE DATABASE IF NOT EXISTS `agriculture_machinery_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
conn.commit()
cur.close()
conn.close()
print('Database ensured')
