from collections.abc import Callable
import sqlite3
from unittest.mock import Mock

from fastapi.testclient import TestClient

from models.movie import Movie


def test_home_returns_catalog(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.list_saved_movies.return_value = [movie_factory(id=1)]

    response = client.get("/")

    assert response.status_code == 200
    assert "Movie Manager" in response.text
    assert "Interstellar" in response.text


def test_home_returns_503_when_database_fails(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.list_saved_movies.side_effect = sqlite3.Error("Falha no banco")

    response = client.get("/")

    assert response.status_code == 503
    assert "Falha no banco" in response.text


def test_search_uses_saved_movie_without_calling_api(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory(id=1, avaliation=4)
    web_service_mock.search_movie.return_value = movie

    response = client.get("/search", params={"title": "Interstellar"})

    assert response.status_code == 200
    assert "Interstellar" in response.text
    assert "4/5" in response.text
    web_service_mock.search_api.assert_not_called()


def test_search_uses_api_when_movie_is_not_saved(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.search_movie.return_value = None
    web_service_mock.search_api.return_value = movie_factory(id=None)

    response = client.get("/search", params={"title": "Interstellar"})

    assert response.status_code == 200
    assert "Este filme não foi salvo localmente" in response.text
    web_service_mock.search_api.assert_called_once_with("Interstellar")


def test_search_returns_400_for_invalid_title(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_movie.side_effect = ValueError("O título não pode ser vazio.")

    response = client.get("/search", params={"title": ""})

    assert response.status_code == 400
    assert "O título não pode ser vazio" in response.text


def test_search_returns_503_when_api_is_unavailable(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_movie.return_value = None
    web_service_mock.search_api.side_effect = ConnectionError("API indisponível")

    response = client.get("/search", params={"title": "Interstellar"})

    assert response.status_code == 503
    assert "API indisponível" in response.text


def test_search_returns_503_when_database_fails(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_movie.side_effect = sqlite3.Error("Falha no banco")

    response = client.get("/search", params={"title": "Interstellar"})

    assert response.status_code == 503
    assert "Não foi possível acessar o banco de dados" in response.text


def test_search_without_title_returns_422(client: TestClient) -> None:
    response = client.get("/search")

    assert response.status_code == 422


def test_save_existing_movie_redirects_without_calling_api(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.search_movie.return_value = movie_factory(id=1)

    response = client.post(
        "/movies/save",
        data={"title": "Interstellar"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/search?title=Interstellar"
    web_service_mock.search_api.assert_not_called()
    web_service_mock.save_movie.assert_not_called()


def test_save_new_movie_calls_api_and_service(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory(id=None)
    web_service_mock.search_movie.return_value = None
    web_service_mock.search_api.return_value = movie

    response = client.post(
        "/movies/save",
        data={"title": "Interstellar"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    web_service_mock.search_api.assert_called_once_with("Interstellar")
    web_service_mock.save_movie.assert_called_once_with(movie)


def test_save_movie_returns_400_for_validation_error(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_movie.side_effect = ValueError("Título inválido")

    response = client.post("/movies/save", data={"title": "   "})

    assert response.status_code == 400
    assert "Título inválido" in response.text


def test_update_rating_redirects_after_success(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    response = client.post(
        "/movies/1/update-rating",
        data={"rating": "5", "title": "Interstellar"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/search?title=Interstellar"
    web_service_mock.new_review_movie.assert_called_once_with(1, 5)


def test_update_rating_returns_400_for_invalid_review(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.new_review_movie.side_effect = ValueError("Avaliação inválida")
    web_service_mock.search_movie_by_id.return_value = movie_factory(id=1)

    response = client.post(
        "/movies/1/update-rating",
        data={"rating": "5", "title": "Interstellar"},
    )

    assert response.status_code == 400
    assert "Avaliação inválida" in response.text


def test_update_comment_redirects_after_success(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    response = client.post(
        "/movies/1/update-comment",
        data={"comment": "Excelente", "title": "Interstellar"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    web_service_mock.new_comment_movie.assert_called_once_with(1, "Excelente")


def test_update_comment_returns_400_for_invalid_comment(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.new_comment_movie.side_effect = ValueError("Comentário inválido")
    web_service_mock.search_movie_by_id.return_value = movie_factory(id=1)

    response = client.post(
        "/movies/1/update-comment",
        data={"comment": "   ", "title": "Interstellar"},
    )

    assert response.status_code == 400
    assert "Comentário inválido" in response.text


def test_delete_movie_redirects_after_success(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    response = client.post("/movies/1/delete-movie", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    web_service_mock.delete_saved_movie.assert_called_once_with(1)


def test_delete_movie_returns_400_when_movie_is_missing(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.delete_saved_movie.side_effect = ValueError("Filme não encontrado")

    response = client.post("/movies/999/delete-movie")

    assert response.status_code == 400
    assert "Filme não encontrado" in response.text


def test_movie_details_returns_saved_movie(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.search_movie_by_id.return_value = movie_factory(id=1)

    response = client.get("/movies/1")

    assert response.status_code == 200
    assert "Detalhes do filme" in response.text
    assert "Interstellar" in response.text


def test_movie_details_returns_404_when_missing(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_movie_by_id.return_value = None

    response = client.get("/movies/999")

    assert response.status_code == 404
    assert "O filme solicitado não foi encontrado" in response.text
