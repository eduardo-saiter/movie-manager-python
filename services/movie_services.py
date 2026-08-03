from models.movie import Movie
from clients.movie_api_client import MovieApiClient
from repositories.movies_repository import MovieRepository
from utils.exhibition import show_movie
import requests


class MovieServices:

    def __init__(self, api_client: MovieApiClient, repository: MovieRepository) -> None:
        self.api_client = api_client
        self.repository = repository

    def search_movie(self, user_search: str) -> Movie:

        if not user_search:
            raise ValueError("O título não pode ser vazio.")

        movie = self.repository.search_data_movie(user_search)

        if movie is not None:
            return movie
        else:
            print("Este livro não esta no banco de dados.")
        try:
            data = self.api_client.search_api(user_search)
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
        return Movie(
            title=data["Title"],
            year=data["Year"],
            genre=data["Genre"],
            director=data["Director"],
            plot=data["Plot"],
        )

    def save_movie(self, movie: Movie) -> None:
            self.repository.save_movie(movie)

    def list_saved_movies(self) -> None:
        movies = self.repository.list_movies()
        if not movies:
            print("Nenhum filme cadastrado.")
        else:
            print("\nFilmes Cadastrados:")
            count = 0
            for movie in movies:
                count = 1 + count
                print(f"{count}. {movie.title}")

    def new_review_movie(self, user_review: int, movie: Movie) -> None:
        if not user_review:
            raise ValueError("O review não pode ser vazio.")
        try:
            user_review = int(user_review)
        except:
            raise ValueError("Insira um número válido")
        if user_review > 5 or user_review < 0:
            print("Review inválida.")
        else:
            id_movie = movie.id
            self.repository.update_review(user_review, id_movie)

    def new_comment_movie(self, user_comment: str, movie: Movie) -> None:
        if not user_comment:
            raise ValueError("O novo comentário não pode ser vazio")
        else:
            id_movie = movie.id
            self.repository.update_comment(user_comment, id_movie)
            print("Comentário adicionado com sucesso")

    def delete_saved_movie(self, id_movie) -> None:
         self.repository.delete_movie(id_movie)

    def details_movie(self, movie) -> None:
        show_movie(movie)
