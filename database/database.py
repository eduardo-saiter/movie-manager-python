import sqlite3
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent
DB_PATH = BASE_PATH / "movie_manager.db"

def connect() -> sqlite3.Connection:
    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
    )

def initialize_database(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript('''
CREATE TABLE IF NOT EXISTS movies(

    title TEXT NOT NULL UNIQUE COLLATE NOCASE,
    year INTEGER NOT NULL,
    genre TEXT NOT NULL,
    director TEXT NOT NULL,
    plot TEXT NOT NULL,
    poster TEXT,
    comment TEXT,
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    avaliation INTEGER NOT NULL DEFAULT 0
);
    ''')

    conn.commit()