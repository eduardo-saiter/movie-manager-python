from dotenv import load_dotenv
import os
import requests

load_dotenv()
# "https://localhost:9999/"
# "https://www.omdbapi.com/?apikey="


class MovieApiClient:

    def __init__(self) -> None:
        self.api_key = os.getenv("OMDB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OMDB_API_KEY não encontrada."
            )
        
        self.base_url = "https://www.omdbapi.com/"
        

    def search_api(self, user_search: str) -> dict:

        params = {
        "apikey": self.api_key,
        "t": user_search
        }

        response = requests.get(self.base_url,params=params, timeout=10)
        response.raise_for_status()

        return response.json()
