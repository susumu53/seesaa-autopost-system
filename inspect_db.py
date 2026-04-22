import sqlite3
import os

db_path = 'storage.db'
if not os.path.exists(db_path):
    print(f"File {db_path} does not exist.")
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("--- Tables ---")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    for t in tables:
        print(f"Table: {t[0]}")
        cur.execute(f"PRAGMA table_info({t[0]})")
        print(f"  Columns: {[c[1] for c in cur.fetchall()]}")
    
    if ('analyses',) in tables:
        print("\n--- Recent Analyses ---")
        cur.execute("SELECT * FROM analyses ORDER BY created_at DESC LIMIT 10")
        for row in cur.fetchall():
            print(row)
    
    if ('posts',) in tables:
        print("\n--- Recent Posts ---")
        cur.execute("SELECT * FROM posts ORDER BY timestamp DESC LIMIT 10")
        for row in cur.fetchall():
            print(row)

    if ('requests',) in tables:
        print("\n--- Pending Requests ---")
        cur.execute("SELECT * FROM requests WHERE status='pending' LIMIT 5")
        for row in cur.fetchall():
            print(row)
