from dataclasses import dataclass

from models.media import Media


@dataclass(kw_only=True)
class Series(Media):
    total_seasons: int | None = None