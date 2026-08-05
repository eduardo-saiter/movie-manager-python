import os

import requests
from dotenv import load_dotenv

load_dotenv()


class MovieApiClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OMDB_API_KEY")
        if not self.api_key:
            raise ValueError("OMDB_API_KEY não encontrada.")

        self.base_url = "https://www.omdbapi.com/"

    def search_api(self, user_search: str) -> dict:
        params = {
            "apikey": self.api_key,
            "t": user_search,
            "type": "movie",
            "plot": "full",
        }

        response = requests.get(
            self.base_url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def search_many(
        self,
        user_search: str,
        page: int = 1,
    ) -> dict:
        if not 1 <= page <= 100:
            raise ValueError("A página da OMDb deve estar entre 1 e 100.")

        params = {
            "apikey": self.api_key,
            "s": user_search,
            "type": "movie",
            "page": page,
        }

        response = requests.get(
            self.base_url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def search_by_imdb_id(self, imdb_id: str) -> dict:
        params = {
            "apikey": self.api_key,
            "i": imdb_id,
            "type": "movie",
            "plot": "full",
        }

        response = requests.get(
            self.base_url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
