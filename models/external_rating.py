from dataclasses import dataclass


@dataclass(kw_only=True)
class ExternalRating:
    source: str
    value: str

    normalized_score: float | None = None
    media_id: int | None = None
    id: int | None = None