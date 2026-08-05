from dataclasses import dataclass

from models.media import Media


@dataclass(kw_only=True)
class Episode(Media):
    series_id: int | None = None
    season_number: int | None = None
    episode_number: int | None = None