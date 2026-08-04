from unittest.mock import Mock

import pytest
import requests

import clients.movie_api_client as movie_api_client_module
from clients.movie_api_client import MovieApiClient


def test_init_raises_when_api_key_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OMDB_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OMDB_API_KEY não encontrada"):
        MovieApiClient()


def test_search_api_returns_json_and_uses_expected_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OMDB_API_KEY", "fake-api-key")
    expected_data = {
        "Response": "True",
        "Title": "Interstellar",
        "Year": "2014",
    }

    response_mock = Mock()
    response_mock.json.return_value = expected_data
    get_mock = Mock(return_value=response_mock)
    monkeypatch.setattr(movie_api_client_module.requests, "get", get_mock)

    client = MovieApiClient()
    result = client.search_api("Interstellar")

    assert result == expected_data
    get_mock.assert_called_once_with(
        "https://www.omdbapi.com/",
        params={"apikey": "fake-api-key", "t": "Interstellar"},
        timeout=10,
    )
    response_mock.raise_for_status.assert_called_once_with()
    response_mock.json.assert_called_once_with()


def test_search_api_propagates_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OMDB_API_KEY", "fake-api-key")
    response_mock = Mock()
    response_mock.raise_for_status.side_effect = requests.HTTPError("HTTP 500")
    monkeypatch.setattr(
        movie_api_client_module.requests,
        "get",
        Mock(return_value=response_mock),
    )

    client = MovieApiClient()

    with pytest.raises(requests.HTTPError, match="HTTP 500"):
        client.search_api("Interstellar")
