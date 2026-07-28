from dataclasses import dataclass

@dataclass
class Movie:
    title: str
    year: str
    genre: str
    director: str
    plot: str
    id: int | None = None
    avaliation: int | None = None