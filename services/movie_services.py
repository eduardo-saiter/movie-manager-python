from models.movie import Movie
from clients.movie_api_client import MovieApiClient
import requests




class MovieServices:

    def __init__(self, api_client: MovieApiClient) -> None:
        self.api_client = api_client


    def search_movie(self, user_search: str) -> Movie | None:

        if not user_search:
            raise ValueError("O título não pode ficar vazio")

        try:
            data = self.api_client.search_api(user_search)
        except requests.RequestException as error:
            raise ConnectionError(
                "Não foi possível acessar a API."
            ) from error

        if data.get("Response") == "False":
            raise ValueError(
                data.get("Error", "Filme não encontrado")
            )

        return Movie(
            title=data["Title"],
            year=data["Year"],
            genre=data["Genre"],
            director=data["Director"],
            plot=data["Plot"]
        )
