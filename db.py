import os
import sqlite3

DATABASE_PATH = os.environ.get('DATABASE_PATH', 'crawler_results.db')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = dict_factory
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # Create crawler_runs table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS crawler_runs (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            subreddit TEXT NOT NULL,
            posts_count INTEGER NOT NULL,
            keyword TEXT,
            results_count INTEGER NOT NULL
        );
    ''')
    
    # Create crawler_results table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS crawler_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            score INTEGER NOT NULL,
            author TEXT NOT NULL,
            created_utc TEXT NOT NULL,
            num_comments INTEGER NOT NULL,
            summary TEXT,
            top_comments TEXT,
            FOREIGN KEY (run_id) REFERENCES crawler_runs (id)
        );
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
