import sqlite3

from models.movie import Movie
from repositories.movies_repository import MovieRepository


def test_insert_movie(
    conn: sqlite3.Connection,
    movie_repository: MovieRepository,
) -> None:
    movie = Movie(
        title="Interstellar",
        year="2014",
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
    )

    movie_repository.save_movie(movie)

    row = conn.execute(
        """
        SELECT title, year, genre, director, plot
        FROM movies
        WHERE title = ?
        """,
        (movie.title,),
    ).fetchone()

    assert row == (
        "Interstellar",
        2014,
        "Adventure, Drama, Sci-Fi",
        "Christopher Nolan",
        "buraco de minhoca",
    )

def test_list_movies(movie_repository: MovieRepository) -> None:
    movie = Movie(
            title="Interstellar",
            year=2014,
            genre="Adventure, Drama, Sci-Fi",
            director="Christopher Nolan",
            plot="buraco de minhoca",
        )
    
    movie_repository.save_movie(movie)

    result = movie_repository.list_movies()

    assert result == [Movie(title='Interstellar',
        year=2014,
        genre='Adventure, Drama, Sci-Fi',
        director='Christopher Nolan',
        plot='buraco de minhoca',
        id=1,
        avaliation=0,)]