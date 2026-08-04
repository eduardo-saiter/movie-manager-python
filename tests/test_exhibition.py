from collections.abc import Callable

from models.movie import Movie
from utils.exhibition import menu, show_list_movies, show_movie


def test_menu_prints_all_options(capsys) -> None:
    menu()

    output = capsys.readouterr().out
    assert "1. Search movie" in output
    assert "6. Exit" in output


def test_show_movie_prints_stars_and_comment(
    capsys,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory(avaliation=4, comment="Excelente")

    show_movie(movie)

    output = capsys.readouterr().out
    assert "Título: Interstellar" in output
    assert "Avaliação: ⭐⭐⭐⭐☆ (4/5)" in output
    assert "Comentário: Excelente" in output


def test_show_list_movies_prints_empty_message(capsys) -> None:
    show_list_movies([])

    assert "Nenhum filme cadastrado" in capsys.readouterr().out


def test_show_list_movies_numbers_movies(
    capsys,
    movie_factory: Callable[..., Movie],
) -> None:
    show_list_movies(
        [
            movie_factory(title="Interstellar"),
            movie_factory(title="Arrival"),
        ]
    )

    output = capsys.readouterr().out
    assert "1. Interstellar" in output
    assert "2. Arrival" in output
