from models.movie import Movie
from clients.movie_api_client import MovieApiClient
from repositories.movies_repository import MovieRepository
import requests
import sqlite3


class MovieServices:
    def __init__(self, api_client: MovieApiClient, repository: MovieRepository) -> None:
        self.api_client = api_client
        self.repository = repository

    def search_movie(self, user_search: str) -> Movie | None:

        if not user_search.strip():
            raise ValueError("O título não pode ser vazio.")
        
        return self.repository.search_data_movie(user_search)

    def search_movie_by_id(self, movie_id: int) -> Movie | None:

        return self.repository.search_data_movie_id(movie_id)



    def search_api(self,user_search:str) -> Movie:

        try:
            data = self.api_client.search_api(user_search.strip())

        except requests.Timeout as error:
            raise ConnectionError(
                "A API demorou demais para responder."
            ) from error
        
        except requests.ConnectionError as error:
            raise ConnectionError(
                "Não foi possível acessar a API, verifique sua internet."
            ) from error
        
        except requests.RequestException as error:
            raise ConnectionError(
                "Ocorreu um erro durante a comunicação com a API."
            ) from error
        
        if data.get("Response") == "False":
            raise ValueError(
                "Filme não encontrado"
            )
        
        poster = data.get("Poster")

        if poster == "N/A":
            poster = None

        return Movie(
            title=data["Title"],
            year=data["Year"],
            genre=data["Genre"],
            director=data["Director"],
            plot=data["Plot"],
            poster=poster
        )

    def save_movie(self, movie: Movie) -> None:
            
            try:
                self.repository.save_movie(movie)

            except sqlite3.IntegrityError as error:
                raise ValueError(
                    "Este filme já está salvo no catálogo."
                ) from error

    def list_saved_movies(self) -> list[Movie]:
        return self.repository.list_movies()

    def new_review_movie(self, movie_id: int,user_review: int | str) -> None:

        movie = self.search_movie_by_id(movie_id)

        if movie is None:
            raise ValueError("O filme escolhido não foi encontrado")
        
        if (
            isinstance(user_review, str)
            and not user_review.strip()
        ):
            raise ValueError("A avaliação não pode estar vazia.")
        
        try:
            user_review = int(user_review)

        except ValueError as error:
            raise ValueError("Insira um número válido") from error
        
        if not 0 <= user_review <= 5:
            raise ValueError("A avaliação deve estar entre 0 e 5 estrelas.")
        
        self.repository.update_review(user_review, movie_id)

    def new_comment_movie(self, movie_id: int ,user_comment: str) -> None:
            
            movie = self.search_movie_by_id(movie_id)

            if movie is None:
                raise ValueError(
                    "O filme escolhido não foi encontrado."
                )

            comment = user_comment.strip()

            if not comment:
                raise ValueError(
                    "O novo comentário não pode ser vazio."
                )

            if len(comment) > 500:
                raise ValueError(
                    "O comentário deve ter no máximo 500 caracteres."
                )

            self.repository.update_comment(comment, movie_id)

    def delete_saved_movie(self, movie_id) -> None:
        movie = self.search_movie_by_id(movie_id)
        if movie:
            self.repository.delete_movie(movie_id)
        else:
            raise ValueError("O filme escolhido não foi encontrado")

