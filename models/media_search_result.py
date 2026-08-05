from dataclasses import dataclass


@dataclass(kw_only=True)
class MediaSearchResult:
    title: str
    media_type: str

    year: str | None = None
    imdb_id: str | None = None
    poster: str | None = None
    local_id: int | None = None