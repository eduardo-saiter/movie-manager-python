import sqlite3

from fastapi.testclient import TestClient

from database.database import initialize_database
from repositories.movies_repository import MovieRepository
from services.movie_services import MovieServices
from web_app import app
from web_dependencies import get_movie_service


class FakeMovieApiClient:
    def search_many(self, user_search: str, page: int = 1) -> dict:
        assert user_search == "inter"
        assert page == 1
        return {
            "Response": "True",
            "totalResults": "1",
            "Search": [
                {
                    "Title": "Interstellar",
                    "Year": "2014",
                    "imdbID": "tt0816692",
                    "Type": "movie",
                    "Poster": "https://example.com/interstellar.jpg",
                }
            ],
        }

    def search_by_imdb_id(self, imdb_id: str) -> dict:
        assert imdb_id == "tt0816692"
        return {
            "Response": "True",
            "Title": "Interstellar",
            "Year": "2014",
            "Genre": "Adventure, Drama, Sci-Fi",
            "Director": "Christopher Nolan",
            "Plot": "Exploradores atravessam um buraco de minhoca.",
            "Type": "movie",
            "imdbID": "tt0816692",
            "Poster": "https://example.com/interstellar.jpg",
            "Runtime": "169 min",
            "Released": "07 Nov 2014",
            "imdbRating": "8.7",
            "imdbVotes": "2,400,000",
            "Metascore": "74",
            "BoxOffice": "$188,020,017",
            "Ratings": [
                {
                    "Source": "Internet Movie Database",
                    "Value": "8.7/10",
                }
            ],
        }


def test_complete_web_flow_from_omdb_search_to_delete() -> None:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    initialize_database(conn)
    service = MovieServices(
        FakeMovieApiClient(),  # type: ignore[arg-type]
        MovieRepository(conn),
    )
    app.dependency_overrides[get_movie_service] = lambda: service

    try:
        with TestClient(app) as client:
            search_response = client.get(
                "/search",
                params={"title": "inter"},
            )
            assert search_response.status_code == 200
            assert "/omdb/tt0816692" in search_response.text

            external_details = client.get("/omdb/tt0816692")
            assert external_details.status_code == 200
            assert "Adicionar ao catálogo" in external_details.text

            save_response = client.post(
                "/movies/save",
                data={"imdb_id": "tt0816692"},
                follow_redirects=False,
            )
            assert save_response.status_code == 303
            assert save_response.headers["location"] == "/movies/1"

            local_search = client.get(
                "/search",
                params={"title": "inter"},
            )
            assert local_search.status_code == 200
            assert "/movies/1" in local_search.text
            assert "/omdb/tt0816692" not in local_search.text

            rating_response = client.post(
                "/movies/1/update-rating",
                data={"rating": "5"},
                follow_redirects=False,
            )
            assert rating_response.status_code == 303

            comment_response = client.post(
                "/movies/1/update-comment",
                data={"comment": "Excelente"},
                follow_redirects=False,
            )
            assert comment_response.status_code == 303

            local_details = client.get("/movies/1")
            assert local_details.status_code == 200
            assert "(5/5)" in local_details.text
            assert "Excelente" in local_details.text
            assert "8.7/10" in local_details.text

            delete_response = client.post(
                "/movies/1/delete-movie",
                follow_redirects=False,
            )
            assert delete_response.status_code == 303
            assert service.search_movie_by_id(1) is None
    finally:
        app.dependency_overrides.clear()
        conn.close()
