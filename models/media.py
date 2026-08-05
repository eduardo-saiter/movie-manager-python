from dataclasses import dataclass, field
from datetime import date, datetime
from models.external_rating import ExternalRating


@dataclass(kw_only=True)
class Media:
    title: str
    year: int
    genre: str
    plot: str
    media_type: str

    imdb_id: str | None = None
    poster: str | None = None
    awards: str | None = None
    runtime_minutes: int | None = None
    released_at: date | None = None

    imdb_rating: float | None = None
    imdb_votes: int | None = None
    metascore: int | None = None
    box_office: int | None = None
    budget: int | None = None

    comment: str | None = None
    avaliation: int = 0

    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    external_ratings: list[ExternalRating] = field(
        default_factory=list
    )