from unittest.mock import Mock
import pytest
import requests

from models.movie import Movie

from services.movie_services import MovieServices
from repositories.movies_repository import MovieRepository

def test_search_data_movie_returns_movie( api_client_mock: Mock ,movie_repository: MovieRepository) -> None:

    movie_service = MovieServices(
        api_client = api_client_mock,
        repository = movie_repository)
    
    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=5,

    )

    movie_repository.save_movie(movie)

    result = movie_service.search_movie("Interstellar")

    assert result == Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        id=1,
        avaliation=5,
    )

    api_client_mock.search_api.assert_not_called()

def test_search_data_movie_capslock_returns_movie( api_client_mock: Mock, movie_repository: MovieRepository) -> None:
    movie_service = MovieServices(
        api_client = api_client_mock,
        repository = movie_repository)
    
    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=5
    )

    movie_repository.save_movie(movie)

    result = movie_service.search_movie("INTERSTELLAR")

    assert result == Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        id=1,
        avaliation=5,
    )

def test_search_movie_return_nonexistent(api_client_mock:Mock, movie_service: MovieServices) -> None:
    api_client_mock.search_api.return_value = {
        "Response": "False",
        "Error": "Movie not found!",
    }

    with pytest.raises(ValueError, match="Filme não encontrado"):
        movie_service.search_movie("Filme inexistente")

def test_search_movie_empty_title(api_client_mock:Mock, movie_service: MovieServices) -> None:

    with pytest.raises(ValueError, match="O título não pode ser vazio",):
        movie_service.search_movie("")

    api_client_mock.search_api.assert_not_called()

def test_search_movie_api_timeout(api_client_mock:Mock, movie_service: MovieServices) -> None:

    api_client_mock.search_api.side_effect = requests.Timeout()

    with pytest.raises(ConnectionError, match="A API demorou demais para responder"):
        movie_service.search_movie("Interstellar")

def test_search_movie_returns_saved_movie_without_calling_api(
    api_client_mock: Mock,
    movie_repository_mock: Mock,
    movie_service: MovieServices,
) -> None:
    from models.movie import Movie

    saved_movie = Movie(
        title="Interstellar",
        year="2014",
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="A team travels through a wormhole in space.",
        id=1,
        avaliation=0,
    )
    movie_repository_mock.search_data_movie.return_value = saved_movie

    result = movie_service.search_movie("Interstellar")

    assert result is saved_movie
    movie_repository_mock.search_data_movie.assert_called_once_with("Interstellar")
    api_client_mock.search_api.assert_not_called()

##