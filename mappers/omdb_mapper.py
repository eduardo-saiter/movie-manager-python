import re
from datetime import date, datetime

from models.external_rating import ExternalRating
from models.media_search_result import MediaSearchResult
from models.movie import Movie


def _clean_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    cleaned = value.strip()
    if not cleaned or cleaned == "N/A":
        return None

    return cleaned


def _parse_year(value: object) -> int | None:
    text = _clean_text(value)
    if text is None:
        return None

    match = re.search(r"\d{4}", text)
    return int(match.group()) if match is not None else None


def _parse_integer(value: object) -> int | None:
    text = _clean_text(value)
    if text is None:
        return None

    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


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
        return datetime.strptime(text, "%d %b %Y").date()
    except ValueError:
        return None


def _normalize_rating(value: str) -> float | None:
    normalized_value = value.strip()

    if normalized_value.endswith("%"):
        try:
            return float(normalized_value.removesuffix("%"))
        except ValueError:
            return None

    match = re.fullmatch(
        r"([\d.]+)\s*/\s*([\d.]+)",
        normalized_value,
    )
    if match is None:
        return None

    try:
        score = float(match.group(1))
        maximum = float(match.group(2))
    except ValueError:
        return None

    if maximum == 0:
        return None

    return round(score / maximum * 100, 2)


def _build_external_ratings(data: dict) -> list[ExternalRating]:
    ratings = data.get("Ratings", [])
    if not isinstance(ratings, list):
        return []

    result: list[ExternalRating] = []
    seen_sources: set[str] = set()

    for item in ratings:
        if not isinstance(item, dict):
            continue

        source = _clean_text(item.get("Source"))
        value = _clean_text(item.get("Value"))
        if source is None or value is None:
            continue

        source_key = source.casefold()
        if source_key in seen_sources:
            continue

        seen_sources.add(source_key)

        result.append(
            ExternalRating(
                source=source,
                value=value,
                normalized_score=_normalize_rating(value),
            )
        )

    return result


def _omdb_error_message(data: dict) -> str:
    message = _clean_text(data.get("Error"))
    if message == "Movie not found!":
        return "Filme não encontrado."
    return message or "Filme não encontrado."


def map_movie_from_omdb(data: dict) -> Movie:
    if data.get("Response") == "False":
        raise ValueError(_omdb_error_message(data))

    media_type = _clean_text(data.get("Type"))
    if media_type != "movie":
        raise ValueError("O resultado encontrado não é um filme.")

    title = _clean_text(data.get("Title"))
    year = _parse_year(data.get("Year"))
    imdb_id = _clean_text(data.get("imdbID"))

    if title is None:
        raise ValueError("A API não retornou o título do filme.")
    if year is None:
        raise ValueError("A API não retornou um ano válido.")
    if imdb_id is None:
        raise ValueError("A API não retornou um IMDb ID válido.")

    return Movie(
        title=title,
        year=year,
        genre=_clean_text(data.get("Genre")) or "Não informado",
        director=_clean_text(data.get("Director")),
        plot=_clean_text(data.get("Plot")) or "Não informado",
        media_type="movie",
        imdb_id=imdb_id,
        poster=_clean_text(data.get("Poster")),
        awards=_clean_text(data.get("Awards")),
        runtime_minutes=_parse_integer(data.get("Runtime")),
        released_at=_parse_date(data.get("Released")),
        imdb_rating=_parse_float(data.get("imdbRating")),
        imdb_votes=_parse_integer(data.get("imdbVotes")),
        metascore=_parse_integer(data.get("Metascore")),
        box_office=_parse_integer(data.get("BoxOffice")),
        budget=None,
        external_ratings=_build_external_ratings(data),
    )


def map_search_results_from_omdb(
    data: dict,
) -> list[MediaSearchResult]:
    if data.get("Response") == "False":
        if _clean_text(data.get("Error")) == "Movie not found!":
            return []
        raise ValueError(_omdb_error_message(data))

    items = data.get("Search", [])
    if not isinstance(items, list):
        return []

    results: list[MediaSearchResult] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        title = _clean_text(item.get("Title"))
        imdb_id = _clean_text(item.get("imdbID"))
        media_type = _clean_text(item.get("Type")) or "movie"

        if title is None or imdb_id is None or media_type != "movie":
            continue

        results.append(
            MediaSearchResult(
                title=title,
                year=_clean_text(item.get("Year")),
                media_type=media_type,
                imdb_id=imdb_id,
                poster=_clean_text(item.get("Poster")),
            )
        )

    return results
