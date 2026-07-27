from unittest.mock import Mock
import requests
import pytest

import clients.movie_api_client as movie_api_client
from clients.movie_api_client import MovieApiClient

def test_search_api_returns_response_data(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OMDB_API_KEY", "fake-api-key")

    expected_data = {
    "Response": "True",
    "Title": "Interstellar",
    "Year": "2014",
}

    response_mock = Mock()
    response_mock.json.return_value = expected_data

    get_mock = Mock(return_value=response_mock)

    monkeypatch.setattr(
    movie_api_client.requests,
    "get",
    get_mock,
    )

    client = MovieApiClient()

    result = client.search_api("Interstellar")

    assert result == expected_data

def test_init_raises_value_error_when_api_key_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:

    monkeypatch.delenv("OMDB_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OMDB_API_KEY não encontrada."):
        MovieApiClient()

def test_search_api_raises_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OMDB_API_KEY", "fake-api-key")
    
    
    response_mock = Mock()
    response_mock.raise_for_status.side_effect = requests.HTTPError()

    get_mock = Mock(return_value=response_mock)

    monkeypatch.setattr(
    movie_api_client.requests,
    "get",
    get_mock,
    )

    client = MovieApiClient()

    with pytest.raises(requests.HTTPError):
        client.search_api("Interstellar")