import sqlite3
from datetime import date, datetime

from models.external_rating import ExternalRating
from models.media_search_result import MediaSearchResult
from models.movie import Movie


class MovieRepository:
    _MOVIE_SELECT = """
        SELECT
            media.id,
            media.imdb_id,
            media.media_type,
            media.title,
            media.year,
            media.genre,
            movie_details.director,
            media.plot,
            media.poster,
            media.awards,
            media.runtime_minutes,
            media.released_at,
            media.imdb_rating,
            media.imdb_votes,
            media.metascore,
            media.box_office,
            media.budget,
            media.comment,
            media.avaliation,
            media.created_at,
            media.updated_at
        FROM media
        INNER JOIN movie_details
            ON movie_details.media_id = media.id
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def _load_external_ratings(
        self,
        media_id: int,
    ) -> list[ExternalRating]:
        rows = self.conn.execute(
            """
            SELECT
                id,
                media_id,
                source,
                value,
                normalized_score
            FROM external_ratings
            WHERE media_id = ?
            ORDER BY id
            """,
            (media_id,),
        ).fetchall()

        return [
            ExternalRating(
                id=row[0],
                media_id=row[1],
                source=row[2],
                value=row[3],
                normalized_score=row[4],
            )
            for row in rows
        ]

    def _row_to_movie(self, row: tuple[object, ...]) -> Movie:
        media_id = int(row[0])

        released_at = (
            date.fromisoformat(str(row[11]))
            if row[11] is not None
            else None
        )
        created_at = (
            datetime.fromisoformat(str(row[19]))
            if row[19] is not None
            else None
        )
        updated_at = (
            datetime.fromisoformat(str(row[20]))
            if row[20] is not None
            else None
        )

        return Movie(
            id=media_id,
            imdb_id=row[1],  # type: ignore[arg-type]
            media_type=str(row[2]),
            title=str(row[3]),
            year=int(row[4]),
            genre=str(row[5]),
            director=row[6],  # type: ignore[arg-type]
            plot=str(row[7]),
            poster=row[8],  # type: ignore[arg-type]
            awards=row[9],  # type: ignore[arg-type]
            runtime_minutes=row[10],  # type: ignore[arg-type]
            released_at=released_at,
            imdb_rating=row[12],  # type: ignore[arg-type]
            imdb_votes=row[13],  # type: ignore[arg-type]
            metascore=row[14],  # type: ignore[arg-type]
            box_office=row[15],  # type: ignore[arg-type]
            budget=row[16],  # type: ignore[arg-type]
            comment=row[17],  # type: ignore[arg-type]
            avaliation=int(row[18]),
            created_at=created_at,
            updated_at=updated_at,
            external_ratings=self._load_external_ratings(media_id),
        )

    def save_movie(self, movie: Movie) -> None:
        rating_ids: list[int] = []

        with self.conn:
            cursor = self.conn.execute(
                """
                INSERT INTO media (
                    imdb_id,
                    media_type,
                    title,
                    year,
                    genre,
                    plot,
                    poster,
                    awards,
                    runtime_minutes,
                    released_at,
                    imdb_rating,
                    imdb_votes,
                    metascore,
                    box_office,
                    budget,
                    comment,
                    avaliation
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    movie.imdb_id,
                    movie.media_type,
                    movie.title,
                    movie.year,
                    movie.genre,
                    movie.plot,
                    movie.poster,
                    movie.awards,
                    movie.runtime_minutes,
                    (
                        movie.released_at.isoformat()
                        if movie.released_at is not None
                        else None
                    ),
                    movie.imdb_rating,
                    movie.imdb_votes,
                    movie.metascore,
                    movie.box_office,
                    movie.budget,
                    movie.comment,
                    movie.avaliation,
                ),
            )

            media_id = cursor.lastrowid
            if media_id is None:
                raise sqlite3.DatabaseError(
                    "Não foi possível obter o ID da mídia."
                )

            self.conn.execute(
                """
                INSERT INTO movie_details (
                    media_id,
                    director
                )
                VALUES (?, ?)
                """,
                (media_id, movie.director),
            )

            for rating in movie.external_ratings:
                rating_cursor = self.conn.execute(
                    """
                    INSERT INTO external_ratings (
                        media_id,
                        source,
                        value,
                        normalized_score
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        media_id,
                        rating.source,
                        rating.value,
                        rating.normalized_score,
                    ),
                )

                if rating_cursor.lastrowid is None:
                    raise sqlite3.DatabaseError(
                        "Não foi possível obter o ID da avaliação externa."
                    )

                rating_ids.append(rating_cursor.lastrowid)

        # Os objetos só recebem IDs depois que toda a transação foi confirmada.
        movie.id = media_id
        for rating, rating_id in zip(
            movie.external_ratings,
            rating_ids,
            strict=True,
        ):
            rating.id = rating_id
            rating.media_id = media_id

    def search_data_movie(self, title: str) -> Movie | None:
        normalized_title = title.strip()
        if not normalized_title:
            return None

        row = self.conn.execute(
            self._MOVIE_SELECT
            + """
            WHERE media.title = ? COLLATE NOCASE
              AND media.media_type = 'movie'
            ORDER BY media.year DESC
            LIMIT 1
            """,
            (normalized_title,),
        ).fetchone()

        return None if row is None else self._row_to_movie(row)

    def search_movie_by_id(self, movie_id: int) -> Movie | None:
        row = self.conn.execute(
            self._MOVIE_SELECT
            + """
            WHERE media.id = ?
              AND media.media_type = 'movie'
            """,
            (movie_id,),
        ).fetchone()

        return None if row is None else self._row_to_movie(row)

    def search_movie_results(
        self,
        user_search: str,
    ) -> list[MediaSearchResult]:
        normalized_search = user_search.strip()
        if not normalized_search:
            return []

        pattern = f"%{normalized_search}%"

        rows = self.conn.execute(
            """
            SELECT
                id,
                imdb_id,
                title,
                year,
                media_type,
                poster
            FROM media
            WHERE title LIKE ? COLLATE NOCASE
              AND media_type = 'movie'
            ORDER BY
                title COLLATE NOCASE,
                year DESC
            """,
            (pattern,),
        ).fetchall()

        return [
            MediaSearchResult(
                local_id=int(row[0]),
                imdb_id=row[1],
                title=str(row[2]),
                year=(str(row[3]) if row[3] is not None else None),
                media_type=str(row[4]),
                poster=row[5],
            )
            for row in rows
        ]

    def find_local_ids_by_imdb_ids(
        self,
        imdb_ids: list[str],
    ) -> dict[str, int]:
        normalized_ids = list(
            dict.fromkeys(
                imdb_id.strip()
                for imdb_id in imdb_ids
                if imdb_id.strip()
            )
        )

        if not normalized_ids:
            return {}

        placeholders = ", ".join("?" for _ in normalized_ids)
        rows = self.conn.execute(
            f"""
            SELECT imdb_id, id
            FROM media
            WHERE media_type = 'movie'
              AND imdb_id IN ({placeholders})
            """,
            normalized_ids,
        ).fetchall()

        return {
            str(imdb_id).casefold(): int(media_id)
            for imdb_id, media_id in rows
            if imdb_id is not None
        }

    def list_movies(self) -> list[Movie]:
        rows = self.conn.execute(
            self._MOVIE_SELECT
            + """
            WHERE media.media_type = 'movie'
            ORDER BY media.title COLLATE NOCASE
            """
        ).fetchall()

        return [self._row_to_movie(row) for row in rows]

    def delete_movie(self, movie_id: int) -> bool:
        with self.conn:
            cursor = self.conn.execute(
                """
                DELETE FROM media
                WHERE id = ?
                  AND media_type = 'movie'
                """,
                (movie_id,),
            )

        return cursor.rowcount > 0

    def update_review(
        self,
        user_review: int,
        movie_id: int,
    ) -> bool:
        with self.conn:
            cursor = self.conn.execute(
                """
                UPDATE media
                SET
                    avaliation = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                  AND media_type = 'movie'
                """,
                (user_review, movie_id),
            )

        return cursor.rowcount > 0

    def update_comment(
        self,
        user_comment: str,
        movie_id: int,
    ) -> bool:
        with self.conn:
            cursor = self.conn.execute(
                """
                UPDATE media
                SET
                    comment = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                  AND media_type = 'movie'
                """,
                (user_comment, movie_id),
            )

        return cursor.rowcount > 0
