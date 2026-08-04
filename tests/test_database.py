import sqlite3

import pytest

from database.database import initialize_database


def test_initialize_database_creates_movies_table() -> None:
    conn = sqlite3.connect(":memory:")

    initialize_database(conn)

    table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'movies'"
    ).fetchone()

    assert table == ("movies",)
    conn.close()


def test_initialize_database_is_idempotent() -> None:
    conn = sqlite3.connect(":memory:")

    initialize_database(conn)
    initialize_database(conn)

    tables = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'movies'"
    ).fetchone()

    assert tables == (1,)
    conn.close()


def test_review_defaults_to_zero(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        INSERT INTO movies (title, year, genre, director, plot)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("Arrival", 2016, "Sci-Fi", "Denis Villeneuve", "Primeiro contato."),
    )
    conn.commit()

    review = conn.execute(
        "SELECT avaliation FROM movies WHERE title = ?",
        ("Arrival",),
    ).fetchone()

    assert review == (0,)


def test_title_unique_is_case_insensitive(conn: sqlite3.Connection) -> None:
    values = ("Arrival", 2016, "Sci-Fi", "Denis Villeneuve", "Primeiro contato.")
    conn.execute(
        """
        INSERT INTO movies (title, year, genre, director, plot)
        VALUES (?, ?, ?, ?, ?)
        """,
        values,
    )

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO movies (title, year, genre, director, plot)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("ARRIVAL", 2016, "Sci-Fi", "Denis Villeneuve", "Outro."),
        )
