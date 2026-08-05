import sqlite3
from pathlib import Path

import pytest

import database.database as database_module
from database.database import initialize_database


EXPECTED_TABLES = {
    "media",
    "movie_details",
    "series",
    "episodes",
    "external_ratings",
}


def test_connect_configures_sqlite_connection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "test.db"
    monkeypatch.setattr(database_module, "DB_PATH", database_path)

    conn = database_module.connect()

    assert database_path.exists()
    assert conn.execute("PRAGMA foreign_keys").fetchone() == (1,)
    assert conn.execute("PRAGMA busy_timeout").fetchone() == (5000,)
    conn.close()


def insert_media(
    conn: sqlite3.Connection,
    *,
    imdb_id: str = "tt1630029",
    title: str = "Avatar: The Way of Water",
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO media (
            imdb_id,
            media_type,
            title,
            year,
            genre,
            plot
        )
        VALUES (?, 'movie', ?, 2022, 'Adventure', 'Plot')
        """,
        (imdb_id, title),
    )
    assert cursor.lastrowid is not None
    return cursor.lastrowid


def test_initialize_database_creates_current_schema() -> None:
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)

    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }

    assert EXPECTED_TABLES <= tables
    conn.close()


def test_initialize_database_is_idempotent() -> None:
    conn = sqlite3.connect(":memory:")

    initialize_database(conn)
    initialize_database(conn)

    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }

    assert EXPECTED_TABLES <= tables
    conn.close()


def test_initialize_database_enables_foreign_keys() -> None:
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)

    assert conn.execute("PRAGMA foreign_keys").fetchone() == (1,)
    conn.close()


def test_review_defaults_to_zero(conn: sqlite3.Connection) -> None:
    media_id = insert_media(conn)

    review = conn.execute(
        "SELECT avaliation FROM media WHERE id = ?",
        (media_id,),
    ).fetchone()

    assert review == (0,)


@pytest.mark.parametrize("column", ["year", "genre", "plot"])
def test_required_movie_fields_reject_null(
    conn: sqlite3.Connection,
    column: str,
) -> None:
    values = {
        "year": (None, "Drama", "Plot"),
        "genre": (2020, None, "Plot"),
        "plot": (2020, "Drama", None),
    }
    year, genre, plot = values[column]

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO media (
                imdb_id,
                media_type,
                title,
                year,
                genre,
                plot
            )
            VALUES (?, 'movie', 'Invalid', ?, ?, ?)
            """,
            (f"tt-null-{column}", year, genre, plot),
        )


def test_review_must_be_between_zero_and_five(
    conn: sqlite3.Connection,
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO media (
                imdb_id,
                media_type,
                title,
                year,
                genre,
                plot,
                avaliation
            )
            VALUES ('tt1', 'movie', 'Invalid', 2020, 'Drama', 'Plot', 6)
            """
        )


def test_imdb_id_unique_is_case_insensitive(
    conn: sqlite3.Connection,
) -> None:
    insert_media(conn, imdb_id="tt0816692", title="Interstellar")

    with pytest.raises(sqlite3.IntegrityError):
        insert_media(conn, imdb_id="TT0816692", title="Interstellar Copy")


def test_delete_media_cascades_to_movie_details_and_ratings(
    conn: sqlite3.Connection,
) -> None:
    media_id = insert_media(conn)
    conn.execute(
        "INSERT INTO movie_details (media_id, director) VALUES (?, ?)",
        (media_id, "James Cameron"),
    )
    conn.execute(
        """
        INSERT INTO external_ratings (media_id, source, value)
        VALUES (?, 'IMDb', '7.5/10')
        """,
        (media_id,),
    )
    conn.commit()

    conn.execute("DELETE FROM media WHERE id = ?", (media_id,))
    conn.commit()

    assert conn.execute(
        "SELECT 1 FROM movie_details WHERE media_id = ?",
        (media_id,),
    ).fetchone() is None
    assert conn.execute(
        "SELECT 1 FROM external_ratings WHERE media_id = ?",
        (media_id,),
    ).fetchone() is None


def test_update_trigger_changes_updated_at(conn: sqlite3.Connection) -> None:
    media_id = insert_media(conn)
    conn.execute(
        "UPDATE media SET updated_at = '2000-01-01 00:00:00' WHERE id = ?",
        (media_id,),
    )
    conn.execute(
        "UPDATE media SET comment = 'Atualizado' WHERE id = ?",
        (media_id,),
    )
    conn.commit()

    updated_at = conn.execute(
        "SELECT updated_at FROM media WHERE id = ?",
        (media_id,),
    ).fetchone()

    assert updated_at is not None
    assert updated_at[0] != "2000-01-01 00:00:00"
