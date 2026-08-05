from collections.abc import Callable
import sqlite3
from unittest.mock import Mock

from fastapi.testclient import TestClient

from errors import MovieAlreadySavedError, MovieNotFoundError
from models.media_search_result import MediaSearchResult
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
    assert "Minha coleção" in response.text
    assert "Encontrar filme" in response.text
    assert "Meu catálogo" in response.text
    assert "1 filme" in " ".join(response.text.split())
    assert "Interstellar" in response.text
    assert '/movies/1' in response.text
    assert '/static/styles.css' in response.text


def test_home_returns_empty_catalog_message(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.list_saved_movies.return_value = []

    response = client.get("/")

    assert response.status_code == 200
    assert "Nenhum filme cadastrado" in response.text


def test_home_returns_503_when_database_fails(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.list_saved_movies.side_effect = sqlite3.Error(
        "Falha no banco"
    )

    response = client.get("/")

    assert response.status_code == 503
    assert "Não foi possível acessar o banco de dados" in response.text
    assert "Falha no banco" not in response.text
    assert "Nenhum filme cadastrado" not in response.text


def test_search_renders_local_and_omdb_results(
    client: TestClient,
    web_service_mock: Mock,
    search_result_factory: Callable[..., MediaSearchResult],
) -> None:
    web_service_mock.search_results.return_value = [
        search_result_factory(local_id=7),
        search_result_factory(
            title="Interstate 60",
            imdb_id="tt0165832",
            local_id=None,
        ),
    ]

    response = client.get("/search", params={"title": "inter"})

    assert response.status_code == 200
    assert "Interstellar" in response.text
    assert "Interstate 60" in response.text
    assert '/movies/7' in response.text
    assert '/omdb/tt0165832' in response.text
    assert "2 resultados" in " ".join(response.text.split())
    assert "Salvo" in response.text
    assert "OMDb" in response.text
    assert "Abrir filme salvo no catálogo" in response.text
    assert "Ver informações e adicionar ao catálogo" in response.text
    web_service_mock.search_results.assert_called_once_with("inter")


def test_search_renders_no_results_message(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_results.return_value = []

    response = client.get("/search", params={"title": "missing"})

    assert response.status_code == 200
    assert "Nenhum resultado encontrado" in response.text


def test_search_returns_400_for_invalid_title(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_results.side_effect = ValueError(
        "O título não pode ser vazio."
    )

    response = client.get("/search", params={"title": ""})

    assert response.status_code == 400
    assert "O título não pode ser vazio" in response.text


def test_search_returns_503_when_api_is_unavailable(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_results.side_effect = ConnectionError(
        "API indisponível"
    )

    response = client.get("/search", params={"title": "Interstellar"})

    assert response.status_code == 503
    assert "API indisponível" in response.text


def test_search_returns_503_without_exposing_database_error(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_results.side_effect = sqlite3.Error(
        "Detalhes internos"
    )

    response = client.get("/search", params={"title": "Interstellar"})

    assert response.status_code == 503
    assert "Não foi possível acessar o banco de dados" in response.text
    assert "Detalhes internos" not in response.text


def test_search_without_title_returns_html_validation_error(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_results.side_effect = ValueError(
        "O título não pode ser vazio."
    )

    response = client.get("/search")

    assert response.status_code == 400
    assert "O título não pode ser vazio" in response.text
    web_service_mock.search_results.assert_called_once_with("")


def test_save_movie_fetches_by_imdb_id_and_redirects_to_saved_id(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory(id=None)
    web_service_mock.search_api_by_imdb_id.return_value = movie

    def assign_id(saved_movie: Movie) -> None:
        saved_movie.id = 3

    web_service_mock.save_movie.side_effect = assign_id

    response = client.post(
        "/movies/save",
        data={"imdb_id": "tt0816692"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/movies/3"
    web_service_mock.search_api_by_imdb_id.assert_called_once_with(
        "tt0816692"
    )
    web_service_mock.save_movie.assert_called_once_with(movie)


def test_save_movie_returns_400_for_validation_error(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_api_by_imdb_id.side_effect = ValueError(
        "IMDb ID inválido."
    )

    response = client.post("/movies/save", data={"imdb_id": "   "})

    assert response.status_code == 400
    assert "IMDb ID inválido" in response.text


def test_save_movie_returns_503_for_database_error(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.search_api_by_imdb_id.return_value = movie_factory()
    web_service_mock.save_movie.side_effect = sqlite3.Error("interno")

    response = client.post(
        "/movies/save",
        data={"imdb_id": "tt0816692"},
    )

    assert response.status_code == 503
    assert "Não foi possível acessar o banco de dados" in response.text
    assert "interno" not in response.text


def test_save_movie_returns_409_when_movie_is_already_saved(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.search_api_by_imdb_id.return_value = movie_factory()
    web_service_mock.save_movie.side_effect = MovieAlreadySavedError(
        "Este filme já está salvo no catálogo."
    )

    response = client.post(
        "/movies/save",
        data={"imdb_id": "tt0816692"},
    )

    assert response.status_code == 409
    assert "já está salvo" in response.text


def test_save_movie_without_imdb_id_returns_html_validation_error(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_api_by_imdb_id.side_effect = ValueError(
        "IMDb ID inválido."
    )

    response = client.post("/movies/save", data={})

    assert response.status_code == 400
    assert "IMDb ID inválido" in response.text
    web_service_mock.search_api_by_imdb_id.assert_called_once_with("")


def test_update_rating_redirects_to_details_after_success(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    response = client.post(
        "/movies/1/update-rating",
        data={"rating": "5"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/movies/1"
    web_service_mock.new_review_movie.assert_called_once_with(1, "5")


def test_update_rating_returns_400_for_non_numeric_value(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.new_review_movie.side_effect = ValueError(
        "A avaliação deve ser um número inteiro."
    )
    web_service_mock.search_movie_by_id.return_value = movie_factory(id=1)

    response = client.post(
        "/movies/1/update-rating",
        data={"rating": "abc"},
    )

    assert response.status_code == 400
    assert "número inteiro" in response.text


def test_update_rating_without_value_returns_html_validation_error(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.new_review_movie.side_effect = ValueError(
        "A avaliação não pode estar vazia."
    )
    web_service_mock.search_movie_by_id.return_value = movie_factory(id=1)

    response = client.post("/movies/1/update-rating", data={})

    assert response.status_code == 400
    assert "não pode estar vazia" in response.text
    web_service_mock.new_review_movie.assert_called_once_with(1, "")


def test_update_rating_returns_400_with_movie_context(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.new_review_movie.side_effect = ValueError(
        "Avaliação inválida"
    )
    web_service_mock.search_movie_by_id.return_value = movie_factory(id=1)

    response = client.post(
        "/movies/1/update-rating",
        data={"rating": "5"},
    )

    assert response.status_code == 400
    assert "Avaliação inválida" in response.text
    assert "Interstellar" in response.text


def test_update_rating_returns_404_when_movie_is_missing(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.new_review_movie.side_effect = MovieNotFoundError(
        "O filme escolhido não foi encontrado."
    )

    response = client.post(
        "/movies/999/update-rating",
        data={"rating": "5"},
    )

    assert response.status_code == 404
    assert "não foi encontrado" in response.text


def test_update_rating_returns_503_for_database_error(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.new_review_movie.side_effect = sqlite3.Error("interno")

    response = client.post(
        "/movies/1/update-rating",
        data={"rating": "5"},
    )

    assert response.status_code == 503
    assert "Não foi possível acessar o banco de dados" in response.text


def test_update_comment_redirects_to_details_after_success(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    response = client.post(
        "/movies/1/update-comment",
        data={"comment": "Excelente"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/movies/1"
    web_service_mock.new_comment_movie.assert_called_once_with(1, "Excelente")


def test_update_comment_without_value_returns_html_validation_error(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.new_comment_movie.side_effect = ValueError(
        "O comentário não pode estar vazio."
    )
    web_service_mock.search_movie_by_id.return_value = movie_factory(id=1)

    response = client.post("/movies/1/update-comment", data={})

    assert response.status_code == 400
    assert "não pode estar vazio" in response.text
    web_service_mock.new_comment_movie.assert_called_once_with(1, "")


def test_update_comment_returns_400_with_movie_context(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.new_comment_movie.side_effect = ValueError(
        "Comentário inválido"
    )
    web_service_mock.search_movie_by_id.return_value = movie_factory(id=1)

    response = client.post(
        "/movies/1/update-comment",
        data={"comment": "   "},
    )

    assert response.status_code == 400
    assert "Comentário inválido" in response.text
    assert "Interstellar" in response.text


def test_update_comment_returns_404_when_movie_is_missing(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.new_comment_movie.side_effect = MovieNotFoundError(
        "O filme escolhido não foi encontrado."
    )

    response = client.post(
        "/movies/999/update-comment",
        data={"comment": "Comentário"},
    )

    assert response.status_code == 404
    assert "não foi encontrado" in response.text


def test_delete_movie_redirects_after_success(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    response = client.post(
        "/movies/1/delete-movie",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    web_service_mock.delete_saved_movie.assert_called_once_with(1)


def test_delete_movie_returns_400_when_movie_is_missing(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.delete_saved_movie.side_effect = ValueError(
        "Filme não encontrado"
    )

    response = client.post("/movies/999/delete-movie")

    assert response.status_code == 400
    assert "Filme não encontrado" in response.text


def test_delete_movie_returns_404_for_catalog_not_found_error(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.delete_saved_movie.side_effect = MovieNotFoundError(
        "Filme não encontrado"
    )

    response = client.post("/movies/999/delete-movie")

    assert response.status_code == 404
    assert "Filme não encontrado" in response.text


def test_delete_movie_returns_503_for_database_error(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.delete_saved_movie.side_effect = sqlite3.Error("interno")

    response = client.post("/movies/1/delete-movie")

    assert response.status_code == 503
    assert "Não foi possível acessar o banco de dados" in response.text


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
    assert 'class="movie-metadata"' in response.text
    assert "Votos no IMDb" in response.text
    assert "Sinopse" in response.text
    assert "Prêmios e indicações" in response.text
    assert "Avaliações externas" in response.text
    assert '/movies/1/update-rating' in response.text
    assert '/movies/1/update-comment' in response.text
    assert '/movies/1/delete-movie' in response.text
    assert "Adicionar ao catálogo" not in response.text


def test_movie_details_returns_404_when_missing(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_movie_by_id.return_value = None

    response = client.get("/movies/999")

    assert response.status_code == 404
    assert "O filme solicitado não foi encontrado" in response.text


def test_movie_details_returns_503_for_database_error(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_movie_by_id.side_effect = sqlite3.Error("interno")

    response = client.get("/movies/1")

    assert response.status_code == 503
    assert "Não foi possível acessar o banco de dados" in response.text


def test_omdb_details_returns_unsaved_movie_and_save_form(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.search_api_by_imdb_id.return_value = movie_factory(id=None)

    response = client.get("/omdb/tt0816692")

    assert response.status_code == 200
    assert "Interstellar" in response.text
    assert "Este filme não foi salvo localmente" in response.text
    assert "Adicionar ao catálogo" in response.text
    assert 'value="tt0816692"' in response.text


def test_omdb_details_returns_404_for_unknown_movie(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_api_by_imdb_id.side_effect = ValueError(
        "Filme não encontrado."
    )

    response = client.get("/omdb/tt0000000")

    assert response.status_code == 404
    assert "Filme não encontrado" in response.text


def test_omdb_details_returns_503_when_api_is_unavailable(
    client: TestClient,
    web_service_mock: Mock,
) -> None:
    web_service_mock.search_api_by_imdb_id.side_effect = ConnectionError(
        "API indisponível"
    )

    response = client.get("/omdb/tt0816692")

    assert response.status_code == 503
    assert "API indisponível" in response.text


def test_home_renders_placeholder_when_movie_has_no_poster(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.list_saved_movies.return_value = [
        movie_factory(id=4, poster=None)
    ]

    response = client.get("/")

    assert response.status_code == 200
    assert 'class="catalog-poster-placeholder"' in response.text
    assert "Sem pôster" in response.text
    assert '/movies/4' in response.text


def test_search_result_without_ids_is_rendered_without_details_link(
    client: TestClient,
    web_service_mock: Mock,
    search_result_factory: Callable[..., MediaSearchResult],
) -> None:
    web_service_mock.search_results.return_value = [
        search_result_factory(
            title="Resultado sem identificador",
            imdb_id=None,
            local_id=None,
        )
    ]

    response = client.get("/search", params={"title": "resultado"})

    assert response.status_code == 200
    assert "Resultado sem identificador" in response.text
    assert 'aria-label="Abrir detalhes de Resultado sem identificador"' not in (
        response.text
    )


def test_search_renders_poster_placeholder_when_poster_is_missing(
    client: TestClient,
    web_service_mock: Mock,
    search_result_factory: Callable[..., MediaSearchResult],
) -> None:
    web_service_mock.search_results.return_value = [
        search_result_factory(poster=None)
    ]

    response = client.get("/search", params={"title": "inter"})

    assert response.status_code == 200
    assert 'class="poster-placeholder"' in response.text
    assert "Sem pôster" in response.text


def test_saved_movie_details_render_current_visual_sections(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.search_movie_by_id.return_value = movie_factory(
        id=8,
        avaliation=4,
        comment="Muito bom",
    )

    response = client.get("/movies/8")

    assert response.status_code == 200
    assert 'class="details-header"' in response.text
    assert 'class="imdb-score"' in response.text
    assert 'class="ratings-grid"' in response.text
    assert "Muito bom" in response.text
    assert "Confirmar exclusão" in response.text


def test_movie_details_render_placeholder_without_poster(
    client: TestClient,
    web_service_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    web_service_mock.search_movie_by_id.return_value = movie_factory(
        id=1,
        poster=None,
    )

    response = client.get("/movies/1")

    assert response.status_code == 200
    assert "details-poster-placeholder" in response.text
    assert "Pôster não disponível para Interstellar" in response.text
