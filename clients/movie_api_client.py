import os

import requests
from dotenv import load_dotenv

from errors import MovieApiConfigurationError

load_dotenv()


class MovieApiClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://www.omdbapi.com/",
    ) -> None:
        configured_key = api_key if api_key is not None else os.getenv(
            "OMDB_API_KEY"
        )
        cleaned_key = configured_key.strip() if configured_key else ""

        self.api_key = cleaned_key or None
        self.base_url = base_url

    def _require_api_key(self) -> str:
        if self.api_key is None:
            raise MovieApiConfigurationError(
                "OMDB_API_KEY não encontrada."
            )

        return self.api_key

    def _request(
        self,
        params: dict[str, object],
    ) -> dict[str, object]:
        request_params = {
            "apikey": self._require_api_key(),
            **params,
        }

        response = requests.get(
            self.base_url,
            params=request_params,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, dict):
            raise requests.RequestException(
                "A OMDb retornou uma resposta inválida."
            )

        return data

    def search_api(self, user_search: str) -> dict[str, object]:
        return self._request(
            {
                "t": user_search,
                "type": "movie",
                "plot": "full",
            }
        )

    def search_many(
        self,
        user_search: str,
        page: int = 1,
    ) -> dict[str, object]:
        if not 1 <= page <= 100:
            raise ValueError("A página da OMDb deve estar entre 1 e 100.")

        return self._request(
            {
                "s": user_search,
                "type": "movie",
                "page": page,
            }
        )

    def search_by_imdb_id(self, imdb_id: str) -> dict[str, object]:
        return self._request(
            {
                "i": imdb_id,
                "type": "movie",
                "plot": "full",
            }
        )
