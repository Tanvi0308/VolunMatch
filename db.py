import sqlite3
import os

DB_FILE = 'volunteer_db.sqlite'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = dict_factory
    return conn

def init_db():
    # Only initialize if it doesn't exist
    if not os.path.exists(DB_FILE):
        print("Initializing database from schema.sql...")
        conn = sqlite3.connect(DB_FILE)
        with open('schema.sql', 'r') as f:
            schema_script = f.read()
            conn.executescript(schema_script)
        conn.commit()
        conn.close()
        print("Database initialized.")
