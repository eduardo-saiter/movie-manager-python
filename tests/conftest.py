from clients.movie_api_client import MovieApiClient
from services.movie_services import MovieServices
from unittest.mock import Mock
import pytest

@pytest.fixture
def api_client_mock() -> Mock:
    return Mock(spec=MovieApiClient)

@pytest.fixture
def movie_service(api_client_mock: Mock) -> MovieServices:
    return MovieServices(api_client_mock)