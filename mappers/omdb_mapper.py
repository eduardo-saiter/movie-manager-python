import re
from datetime import date, datetime

from models.media_search_result import MediaSearchResult
from models.external_rating import ExternalRating
from models.movie import Movie


def _clean_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value or value == "N/A":
        return None

    return value


def _parse_year(value: object) -> int | None:
    text = _clean_text(value)

    if text is None:
        return None

    match = re.search(r"\d{4}", text)

    if match is None:
        return None

    return int(match.group())


def _parse_integer(value: object) -> int | None:
    text = _clean_text(value)

    if text is None:
        return None

    digits = re.sub(r"[^\d]", "", text)

    if not digits:
        return None

    return int(digits)


def _parse_float(value: object) -> float | None:
    text = _clean_text(value)

    if text is None:
        return None

    try:
        return float(text)
    except ValueError:
        return None


def _parse_date(value: object) -> date | None:
    text = _clean_text(value)

    if text is None:
        return None

    try:
        return datetime.strptime(
            text,
            "%d %b %Y",
        ).date()
    except ValueError:
        return None

def _normalize_rating(value: str) -> float | None:
    value = value.strip()

    if value.endswith("%"):
        try:
            return float(value.removesuffix("%"))
        except ValueError:
            return None

    match = re.fullmatch(
        r"([\d.]+)\s*/\s*([\d.]+)",
        value,
    )

    if match is None:
        return None

    score = float(match.group(1))
    maximum = float(match.group(2))

    if maximum == 0:
        return None

    return score / maximum * 100

def _build_external_ratings(
    data: dict,
) -> list[ExternalRating]:
    result: list[ExternalRating] = []

    ratings = data.get("Ratings", [])

    if not isinstance(ratings, list):
        return result

    for item in ratings:
        if not isinstance(item, dict):
            continue

        source = _clean_text(item.get("Source"))
        value = _clean_text(item.get("Value"))

        if source is None or value is None:
            continue

        result.append(
            ExternalRating(
                source=source,
                value=value,
                normalized_score=_normalize_rating(value),
            )
        )

    return result

def map_movie_from_omdb(data: dict) -> Movie:
    if data.get("Response") == "False":
        message = data.get(
            "Error",
            "Filme não encontrado.",
        )

        raise ValueError(message)

    media_type = _clean_text(data.get("Type"))

    if media_type != "movie":
        raise ValueError(
            "O resultado encontrado não é um filme."
        )

    title = _clean_text(data.get("Title"))
    year = _parse_year(data.get("Year"))

    if title is None:
        raise ValueError(
            "A API não retornou o título do filme."
        )

    if year is None:
        raise ValueError(
            "A API não retornou um ano válido."
        )

    return Movie(
        title=title,
        year=year,
        genre=_clean_text(data.get("Genre"))
        or "Não informado",
        director=_clean_text(data.get("Director")),
        plot=_clean_text(data.get("Plot"))
        or "Não informado",
        media_type="movie",
        imdb_id=_clean_text(data.get("imdbID")),
        poster=_clean_text(data.get("Poster")),
        awards=_clean_text(data.get("Awards")),
        runtime_minutes=_parse_integer(
            data.get("Runtime")
        ),
        released_at=_parse_date(
            data.get("Released")
        ),
        imdb_rating=_parse_float(
            data.get("imdbRating")
        ),
        imdb_votes=_parse_integer(
            data.get("imdbVotes")
        ),
        metascore=_parse_integer(
            data.get("Metascore")
        ),
        box_office=_parse_integer(
            data.get("BoxOffice")
        ),
        budget=None,
        external_ratings=_build_external_ratings(
            data
        ),
    )

def map_search_results_from_omdb(data: dict,) -> list[MediaSearchResult]:

    if data.get("Response") == "False":
        error_message = data.get(
            "Error",
            "Nenhuma mídia encontrada.",
        )

        if error_message == "Movie not found!":
            return []
        raise ValueError(error_message)
    
    items = data.get("Search", [])

    if not isinstance(items, list):
        return []
    
    results: list[MediaSearchResult] = []

    for item in items:
        if not isinstance(item, dict):
            continue
        title = _clean_text(item.get("Title"))
        imdb_id = _clean_text(item.get("imdbID"))
        if title is None or imdb_id is None:
            continue
        results.append(
            MediaSearchResult(
                title=title,
                year=_clean_text(item.get("Year")),
                media_type=(
                    _clean_text(item.get("Type"))
                    or "movie"
                ),
                imdb_id=imdb_id,
                poster=_clean_text(item.get("Poster")),
                local_id=None,
            )
        )
        
    return results  