from unittest.mock import Mock

import pytest
import requests

import clients.movie_api_client as movie_api_client_module
from clients.movie_api_client import MovieApiClient


def build_response(data: dict) -> Mock:
    response = Mock()
    response.json.return_value = data
    return response


def test_init_raises_when_api_key_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OMDB_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OMDB_API_KEY não encontrada"):
        MovieApiClient()


def test_search_api_uses_title_movie_and_full_plot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OMDB_API_KEY", "fake-api-key")
    response = build_response({"Response": "True"})
    get_mock = Mock(return_value=response)
    monkeypatch.setattr(movie_api_client_module.requests, "get", get_mock)

    client = MovieApiClient()
    result = client.search_api("Interstellar")

    assert result == {"Response": "True"}
    get_mock.assert_called_once_with(
        "https://www.omdbapi.com/",
        params={
            "apikey": "fake-api-key",
            "t": "Interstellar",
            "type": "movie",
            "plot": "full",
        },
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()


def test_search_many_uses_search_and_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OMDB_API_KEY", "fake-api-key")
    response = build_response({"Search": []})
    get_mock = Mock(return_value=response)
    monkeypatch.setattr(movie_api_client_module.requests, "get", get_mock)

    client = MovieApiClient()
    result = client.search_many("inter", page=2)

    assert result == {"Search": []}
    get_mock.assert_called_once_with(
        "https://www.omdbapi.com/",
        params={
            "apikey": "fake-api-key",
            "s": "inter",
            "type": "movie",
            "page": 2,
        },
        timeout=10,
    )


@pytest.mark.parametrize("page", [0, 101])
def test_search_many_rejects_invalid_page(
    monkeypatch: pytest.MonkeyPatch,
    page: int,
) -> None:
    monkeypatch.setenv("OMDB_API_KEY", "fake-api-key")
    client = MovieApiClient()

    with pytest.raises(ValueError, match="entre 1 e 100"):
        client.search_many("inter", page=page)


def test_search_by_imdb_id_uses_id_and_full_plot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OMDB_API_KEY", "fake-api-key")
    response = build_response({"Response": "True"})
    get_mock = Mock(return_value=response)
    monkeypatch.setattr(movie_api_client_module.requests, "get", get_mock)

    client = MovieApiClient()
    client.search_by_imdb_id("tt0816692")

    get_mock.assert_called_once_with(
        "https://www.omdbapi.com/",
        params={
            "apikey": "fake-api-key",
            "i": "tt0816692",
            "type": "movie",
            "plot": "full",
        },
        timeout=10,
    )


def test_client_propagates_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OMDB_API_KEY", "fake-api-key")
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError("HTTP 500")
    monkeypatch.setattr(
        movie_api_client_module.requests,
        "get",
        Mock(return_value=response),
    )

    with pytest.raises(requests.HTTPError, match="HTTP 500"):
        MovieApiClient().search_api("Interstellar")
