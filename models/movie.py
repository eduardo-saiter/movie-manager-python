from dataclasses import dataclass

@dataclass
class Movie:
    title: str
    year: str
    genre: str
    director: str
    plot: str
    comment : str | None = None
    id: int | None = None
    avaliation: int = 0