from datetime import date

import pytest

from mappers.omdb_mapper import (
    map_movie_from_omdb,
    map_search_results_from_omdb,
)


def full_movie_data(**overrides: object) -> dict:
    data: dict[str, object] = {
        "Response": "True",
        "Title": "Interstellar",
        "Year": "2014",
        "Genre": "Adventure, Drama, Sci-Fi",
        "Director": "Christopher Nolan",
        "Plot": "Exploradores atravessam um buraco de minhoca.",
        "Type": "movie",
        "imdbID": "tt0816692",
        "Poster": "https://example.com/interstellar.jpg",
        "Awards": "1 Oscar",
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
            },
            {
                "Source": "Rotten Tomatoes",
                "Value": "73%",
            },
            {
                "Source": "Metacritic",
                "Value": "74/100",
            },
        ],
    }
    data.update(overrides)
    return data


def test_map_movie_from_omdb_maps_complete_payload() -> None:
    movie = map_movie_from_omdb(full_movie_data())

    assert movie.title == "Interstellar"
    assert movie.year == 2014
    assert movie.media_type == "movie"
    assert movie.runtime_minutes == 169
    assert movie.released_at == date(2014, 11, 7)
    assert movie.imdb_rating == 8.7
    assert movie.imdb_votes == 2_400_000
    assert movie.metascore == 74
    assert movie.box_office == 188_020_017
    assert [rating.normalized_score for rating in movie.external_ratings] == [
        87.0,
        73.0,
        74.0,
    ]


def test_map_movie_converts_na_values_to_none() -> None:
    movie = map_movie_from_omdb(
        full_movie_data(
            Poster="N/A",
            Awards="N/A",
            Runtime="N/A",
            Released="N/A",
            imdbRating="N/A",
            imdbVotes="N/A",
            Metascore="N/A",
            BoxOffice="N/A",
        )
    )

    assert movie.poster is None
    assert movie.awards is None
    assert movie.runtime_minutes is None
    assert movie.released_at is None
    assert movie.imdb_rating is None
    assert movie.imdb_votes is None
    assert movie.metascore is None
    assert movie.box_office is None


def test_map_movie_uses_first_year_from_range() -> None:
    movie = map_movie_from_omdb(full_movie_data(Year="2014–2015"))

    assert movie.year == 2014


def test_map_movie_uses_fallback_for_missing_genre_and_plot() -> None:
    movie = map_movie_from_omdb(
        full_movie_data(Genre="N/A", Plot="N/A")
    )

    assert movie.genre == "Não informado"
    assert movie.plot == "Não informado"


def test_map_movie_translates_not_found_error() -> None:
    with pytest.raises(ValueError, match="Filme não encontrado"):
        map_movie_from_omdb(
            {"Response": "False", "Error": "Movie not found!"}
        )


def test_map_movie_rejects_non_movie_result() -> None:
    with pytest.raises(ValueError, match="não é um filme"):
        map_movie_from_omdb(full_movie_data(Type="series"))


def test_map_movie_rejects_missing_title() -> None:
    with pytest.raises(ValueError, match="título"):
        map_movie_from_omdb(full_movie_data(Title="N/A"))


def test_map_movie_rejects_invalid_year() -> None:
    with pytest.raises(ValueError, match="ano válido"):
        map_movie_from_omdb(full_movie_data(Year="N/A"))


def test_map_movie_skips_invalid_external_ratings() -> None:
    movie = map_movie_from_omdb(
        full_movie_data(
            Ratings=[
                {"Source": "IMDb", "Value": "8/10"},
                {"Source": "N/A", "Value": "50%"},
                "invalid",
            ]
        )
    )

    assert len(movie.external_ratings) == 1
    assert movie.external_ratings[0].source == "IMDb"


def test_map_search_results_returns_movies() -> None:
    results = map_search_results_from_omdb(
        {
            "Response": "True",
            "Search": [
                {
                    "Title": "Interstellar",
                    "Year": "2014",
                    "imdbID": "tt0816692",
                    "Type": "movie",
                    "Poster": "N/A",
                }
            ],
        }
    )

    assert len(results) == 1
    assert results[0].title == "Interstellar"
    assert results[0].poster is None
    assert results[0].local_id is None


def test_map_search_results_ignores_invalid_and_non_movie_items() -> None:
    results = map_search_results_from_omdb(
        {
            "Response": "True",
            "Search": [
                {
                    "Title": "Valid",
                    "Year": "2020",
                    "imdbID": "tt1",
                    "Type": "movie",
                },
                {
                    "Title": "Series",
                    "Year": "2020",
                    "imdbID": "tt2",
                    "Type": "series",
                },
                {"Title": "Missing ID", "Type": "movie"},
                "invalid",
            ],
        }
    )

    assert [result.title for result in results] == ["Valid"]


def test_map_search_results_returns_empty_when_not_found() -> None:
    assert map_search_results_from_omdb(
        {"Response": "False", "Error": "Movie not found!"}
    ) == []


def test_map_search_results_raises_for_other_api_error() -> None:
    with pytest.raises(ValueError, match="Too many results"):
        map_search_results_from_omdb(
            {"Response": "False", "Error": "Too many results."}
        )


def test_map_search_results_returns_empty_for_invalid_search_field() -> None:
    assert map_search_results_from_omdb(
        {"Response": "True", "Search": "invalid"}
    ) == []
