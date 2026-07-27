from unittest.mock import Mock
import pytest
import requests

from services.movie_services import MovieServices

def test_search_movie_return_movie(api_client_mock: Mock, movie_service: MovieServices) -> None:
    api_client_mock.search_api.return_value = {
        "Response": "True",
        "Title": "Interstellar",
        "Year": "2014",
        "Genre": "Adventure, Drama, Sci-Fi",
        "Director": "Christopher Nolan",
        "Plot": "A team travels through a wormhole in space.",
    }

    movie = movie_service.search_movie("Interstellar")

    assert movie.title == "Interstellar"
    assert movie.year == "2014"
    assert movie.director == "Christopher Nolan"

    api_client_mock.search_api.assert_called_once_with("Interstellar")

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