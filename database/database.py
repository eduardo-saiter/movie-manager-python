import sqlite3
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent
DB_PATH = BASE_PATH / "movie_manager.db"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
        timeout=10,
    )
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def initialize_database(conn: sqlite3.Connection) -> None:
    # A conexão de produção já ativa as chaves estrangeiras em connect(),
    # mas fazer isso aqui também mantém conexões de teste seguras.
    conn.execute("PRAGMA foreign_keys = ON")

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            imdb_id TEXT COLLATE NOCASE UNIQUE,
            media_type TEXT NOT NULL
                CHECK (media_type IN ('movie', 'series', 'episode')),

            title TEXT NOT NULL COLLATE NOCASE,
            year INTEGER NOT NULL,
            genre TEXT NOT NULL,
            plot TEXT NOT NULL,
            poster TEXT,
            awards TEXT,

            runtime_minutes INTEGER,
            released_at TEXT,

            imdb_rating REAL,
            imdb_votes INTEGER,
            metascore INTEGER,
            box_office INTEGER,
            budget INTEGER,

            comment TEXT,
            avaliation INTEGER NOT NULL DEFAULT 0
                CHECK (avaliation BETWEEN 0 AND 5),

            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE UNIQUE INDEX IF NOT EXISTS ux_media_imdb_id_nocase
        ON media (LOWER(imdb_id))
        WHERE imdb_id IS NOT NULL;

        CREATE TABLE IF NOT EXISTS movie_details (
            media_id INTEGER PRIMARY KEY,
            director TEXT,

            FOREIGN KEY (media_id)
                REFERENCES media(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS series (
            media_id INTEGER PRIMARY KEY,
            total_seasons INTEGER,

            FOREIGN KEY (media_id)
                REFERENCES media(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS episodes (
            media_id INTEGER PRIMARY KEY,
            series_id INTEGER NOT NULL,
            season_number INTEGER NOT NULL,
            episode_number INTEGER NOT NULL,

            FOREIGN KEY (media_id)
                REFERENCES media(id)
                ON DELETE CASCADE,

            FOREIGN KEY (series_id)
                REFERENCES series(media_id)
                ON DELETE CASCADE,

            UNIQUE (
                series_id,
                season_number,
                episode_number
            )
        );

        CREATE TABLE IF NOT EXISTS external_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            value TEXT NOT NULL,
            normalized_score REAL,

            FOREIGN KEY (media_id)
                REFERENCES media(id)
                ON DELETE CASCADE,

            UNIQUE (media_id, source)
        );

        CREATE TRIGGER IF NOT EXISTS update_media_timestamp
        AFTER UPDATE ON media
        FOR EACH ROW
        WHEN NEW.updated_at = OLD.updated_at
        BEGIN
            UPDATE media
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END;
        """
    )

    conn.commit()
