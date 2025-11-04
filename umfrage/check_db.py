import sqlite3, os

db_path = os.path.join("instance", "flow_study.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("PRAGMA table_info(responses);")
cols = cur.fetchall()

print(">>> Spalten in responses:")
for c in cols:
    print(c[1])

print(">>> Anzahl:", len(cols))
conn.close()
