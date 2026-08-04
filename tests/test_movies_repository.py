import sqlite3
import pytest

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
            comment="bom"
        )
    
    movie_repository.save_movie(movie)

    result = movie_repository.list_movies()

    assert result == [Movie(title='Interstellar',
        year=2014,
        genre='Adventure, Drama, Sci-Fi',
        director='Christopher Nolan',
        plot='buraco de minhoca',
        comment="bom",
        id=1,
        avaliation=0,)]

def test_list_movies_empty_movies(movie_repository: MovieRepository) -> None:
    result = movie_repository.list_movies()
    assert result == []

def test_search_data_movie_return_movie(movie_repository:MovieRepository) -> None:
    movie = Movie(
            title="Interstellar",
            year=2014,
            genre="Adventure, Drama, Sci-Fi",
            director="Christopher Nolan",
            plot="buraco de minhoca",
            comment="bom"
        )
    
    movie_repository.save_movie(movie)

    result = movie_repository.search_data_movie("Interstellar")

    assert result == Movie(
            title="Interstellar",
            year=2014,
            genre="Adventure, Drama, Sci-Fi",
            director="Christopher Nolan",
            plot="buraco de minhoca",
            comment="bom",
            id=1,
            avaliation=0,
    )

def test_search_data_movie_return_None(movie_repository:MovieRepository)-> None:

    result = movie_repository.search_data_movie("Filme Inexistente")

    assert result == None

def test_delete_movie(movie_repository:MovieRepository) -> None:
    movie = Movie(
            title="Interstellar",
            year=2014,
            genre="Adventure, Drama, Sci-Fi",
            director="Christopher Nolan",
            plot="buraco de minhoca",
            comment="bom"
        )
    
    movie_repository.save_movie(movie)
    movie = movie_repository.search_data_movie("Interstellar")
    id_movie = movie.id
    movie_repository.delete_movie(id_movie)
    result = movie_repository.search_data_movie("Interstellar")
    assert result == None

def test_update_review_movie(movie_repository:MovieRepository)-> None:
    movie = Movie(
            title="Interstellar",
            year=2014,
            genre="Adventure, Drama, Sci-Fi",
            director="Christopher Nolan",
            plot="buraco de minhoca",
            comment="bom"
        )
    
    movie_repository.save_movie(movie)
    movie = movie_repository.search_data_movie("Interstellar")
    id_movie = movie.id
    user_review = 5
    movie_repository.update_review(user_review,id_movie)
    result = movie_repository.search_data_movie("Interstellar")

    assert result.avaliation == 5

def test_update_comment_movie(movie_repository:MovieRepository)-> None:
    movie = Movie(
            title="Interstellar",
            year=2014,
            genre="Adventure, Drama, Sci-Fi",
            director="Christopher Nolan",
            plot="buraco de minhoca",
            comment="bom"
        )
    
    movie_repository.save_movie(movie)
    movie = movie_repository.search_data_movie("Interstellar")
    id_movie = movie.id
    user_comment = "ruim"
    movie_repository.update_comment(user_comment,id_movie)
    result = movie_repository.search_data_movie("Interstellar")

    assert result.comment == "ruim"

def test_duplicate_title_raises_integrity_error(
    movie_repository: MovieRepository,
):
    movie1 = Movie(
        title="Interstellar",
        year=2014,
        genre="Sci-Fi",
        director="Christopher Nolan",
        plot="Plot",
    )

    movie2 = Movie(
        title="INTERSTELLAR",
        year=2014,
        genre="Sci-Fi",
        director="Christopher Nolan",
        plot="Plot",
    )

    movie_repository.save_movie(movie1)

    with pytest.raises(sqlite3.IntegrityError):
        movie_repository.save_movie(movie2)