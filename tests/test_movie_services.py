from unittest.mock import Mock
import pytest
import requests

from models.movie import Movie

from services.movie_services import MovieServices
from repositories.movies_repository import MovieRepository


def test_search_movie_returns_movie(api_client_mock: Mock, movie_repository: MovieRepository) -> None:

    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)

    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=5,

    )

    movie_repository.save_movie(movie)

    result = movie_service.search_movie("Interstellar")

    assert result == Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        id=1,
        avaliation=5,
    )

    api_client_mock.search_api.assert_not_called()

def test_search_movie_capslock_returns_movie(api_client_mock: Mock, movie_repository: MovieRepository) -> None:
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)

    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=5
    )

    movie_repository.save_movie(movie)

    result = movie_service.search_movie("INTERSTELLAR")

    assert result == Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        id=1,
        avaliation=5,
    )

def test_search_api_movie_return_nonexistent(api_client_mock: Mock, movie_service: MovieServices) -> None:
    api_client_mock.search_api.return_value = {
        "Response": "False",
        "Error": "Movie not found!",
    }

    with pytest.raises(ValueError, match="Filme não encontrado"):
        movie_service.search_api("Filme inexistente")

def test_search_movie_empty_title(movie_service: MovieServices) -> None:

    with pytest.raises(ValueError, match="O título não pode ser vazio",):
        movie_service.search_movie("")

def test_search_movie_api_timeout(api_client_mock: Mock, movie_service: MovieServices) -> None:

    api_client_mock.search_api.side_effect = requests.Timeout()

    with pytest.raises(ConnectionError, match="A API demorou demais para responder"):
        movie_service.search_api("Interstellar")

def test_search_movie_returns_saved_movie_without_calling_api(
    api_client_mock: Mock,
    movie_repository_mock: Mock,
    movie_service: MovieServices,
) -> None:
    from models.movie import Movie

    saved_movie = Movie(
        title="Interstellar",
        year="2014",
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="A team travels through a wormhole in space.",
        id=1,
        avaliation=0,
    )
    movie_repository_mock.search_data_movie.return_value = saved_movie

    result = movie_service.search_movie("Interstellar")

    assert result is saved_movie
    movie_repository_mock.search_data_movie.assert_called_once_with(
        "Interstellar")
    api_client_mock.search_api.assert_not_called()

def test_list_movies_return_movie(api_client_mock: Mock, movie_repository: MovieRepository) -> None:
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)

    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=5
    )

    movie_service.save_movie(movie)

    result = movie_service.list_saved_movies()

    assert result == [Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        id=1,
        avaliation=5
    )]

def test_list_movies_return_empty(api_client_mock: Mock, movie_repository: MovieRepository) -> None:
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)

    result = movie_service.list_saved_movies()

    assert result == []

def test_update_review_empty_review(movie_repository: MovieRepository, api_client_mock: Mock) -> None:
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)

    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=5,

    )

    movie_service.save_movie(movie)
    movie = movie_service.search_movie("Interstellar")
    with pytest.raises(ValueError, match="A avaliação não pode estar vazia.",):
        movie_service.new_review_movie(movie.id,"")

def test_update_review_invalid_int_review(movie_repository: MovieRepository, api_client_mock: Mock) -> None:
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)

    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=0,
    )

    movie_service.save_movie(movie)
    movie = movie_service.search_movie("Interstellar")
    with pytest.raises(ValueError, match="Insira um número válido",):
        movie_service.new_review_movie(movie.id,"dois")

def test_update_review_invalid_range(movie_repository:MovieRepository, api_client_mock:Mock) -> None:
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)

    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=0,
    )

    movie_service.save_movie(movie)
    movie = movie_service.search_movie("Interstellar")
    with pytest.raises(ValueError, match="A avaliação deve estar entre 0 e 5 estrelas.",):
        movie_service.new_review_movie(movie.id,"-6")

def test_update_review_valid(movie_repository:MovieRepository, api_client_mock:Mock) -> None:
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)

    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=0,
    )

    movie_service.save_movie(movie)
    movie = movie_service.search_movie("Interstellar")
    movie_service.new_review_movie(movie.id,"5")

    result = movie_service.search_movie("Interstellar")

    assert result.avaliation == 5

def test_update_comment_empty_comment(movie_repository: MovieRepository, api_client_mock: Mock) -> None:
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)

    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=0,
    )

    movie_service.save_movie(movie)
    movie = movie_service.search_movie("Interstellar")
    with pytest.raises(ValueError, match="O novo comentário não pode ser vazio",):
        movie_service.new_comment_movie(movie.id,"")

def test_update_comment_valid(movie_repository:MovieRepository, api_client_mock:Mock) -> None:
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)

    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="buraco de minhoca",
        comment="bom",
        avaliation=0,
    )

    movie_service.save_movie(movie)
    movie = movie_service.search_movie("Interstellar")
    movie_service.new_comment_movie(movie.id,"ruim")

    result = movie_service.search_movie("Interstellar")

    assert result.comment == "ruim"

def test_new_review_rejects_value_above_five(movie_repository: MovieRepository, api_client_mock: Mock):
    movie_service = MovieServices(
                api_client=api_client_mock,
                repository=movie_repository)
    movie = Movie(
            title="Interstellar",
            year=2014,
            genre="Adventure, Drama, Sci-Fi",
            director="Christopher Nolan",
            plot="buraco de minhoca",
            comment="bom",
            avaliation=0,
        )
    movie_service.save_movie(movie)
    movie = movie_service.search_movie("Interstellar")

    with pytest.raises(
        ValueError,
        match="A avaliação deve estar entre 0 e 5 estrelas.",
    ):
        movie_service.new_review_movie(1, 6)

def test_new_review_accepts_zero(movie_repository: MovieRepository, api_client_mock: Mock):
    movie_service = MovieServices(
                api_client=api_client_mock,
                repository=movie_repository)
    movie = Movie(
            title="Interstellar",
            year=2014,
            genre="Adventure, Drama, Sci-Fi",
            director="Christopher Nolan",
            plot="buraco de minhoca",
            comment="bom",
            avaliation=0,
        )
    movie_service.save_movie(movie)
    movie = movie_service.search_movie("Interstellar")

    movie_service.new_review_movie(movie.id, 0)

    result = movie_service.search_movie_by_id(movie.id)

    assert result.avaliation == 0

def test_new_comment_removes_extra_spaces(
        movie_repository: MovieRepository, 
        api_client_mock: Mock
):
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)
    
    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Sci-Fi",
        director="Christopher Nolan",
        plot="Plot",
    )

    movie_repository.save_movie(movie)
    movie_service.search_movie("Interstellar")

    movie_service.new_comment_movie(
        movie.id,
        "   Filme excelente!   ",
    )

    result = movie_service.search_movie_by_id(movie.id)

    assert result.comment == "Filme excelente!"

def test_new_review_rejects_non_numeric_value(movie_service):
    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Sci-Fi",
        director="Christopher Nolan",
        plot="Plot",
    )

    movie_service.save_movie(movie)
    movie_service.search_movie("Interstellar")

    with pytest.raises(
        ValueError,
        match="Insira um número válido",
    ):
        movie_service.new_review_movie(1, "cinco")

def test_new_comment_rejects_blank_text(movie_repository: MovieRepository, api_client_mock: Mock):
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)
    
    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Sci-Fi",
        director="Christopher Nolan",
        plot="Plot",
    )

    movie_repository.save_movie(movie)
    movie_service.search_movie("Interstellar")
    with pytest.raises(
        ValueError,
        match="O novo comentário não pode ser vazio",
    ):
        movie_service.new_comment_movie(1, "     ")

def test_new_comment_rejects_long_text(movie_repository: MovieRepository, api_client_mock: Mock):
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)
    
    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Sci-Fi",
        director="Christopher Nolan",
        plot="Plot",
    )

    movie_repository.save_movie(movie)
    movie_service.search_movie("Interstellar")
    with pytest.raises(
        ValueError,
        match="500 caracteres",
    ):
        movie_service.new_comment_movie(1, "a" * 501)

def test_new_comment_nonexistent_movie_raises_error(movie_repository: MovieRepository, api_client_mock: Mock):
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)
    
    movie = Movie(
        title="Interstellar",
        year=2014,
        genre="Sci-Fi",
        director="Christopher Nolan",
        plot="Plot",
    )

    movie_repository.save_movie(movie)
    movie_service.search_movie("Interstellar")
    with pytest.raises(
        ValueError,
        match="não foi encontrado",
    ):
        movie_service.new_comment_movie(999,"bom")

def test_new_review_nonexistent_movie_raises_error(movie_repository: MovieRepository, api_client_mock: Mock):
    movie_service = MovieServices(
        api_client=api_client_mock,
        repository=movie_repository)
    
    with pytest.raises(
        ValueError,
        match="não foi encontrado",
    ):
        movie_service.new_review_movie(999,5)

def test_delete_nonexistent_movie_raises_error(
    movie_repository: MovieRepository, api_client_mock: Mock,
) -> None:
    movie_service = MovieServices(
        api_client= api_client_mock,
        repository= movie_repository
    )
    with pytest.raises(
        ValueError,
        match="não foi encontrado",
    ):
        movie_service.delete_saved_movie(999)