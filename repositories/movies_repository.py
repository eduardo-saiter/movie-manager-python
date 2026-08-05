import sqlite3
from models.movie import Movie
from models.external_rating import ExternalRating
from models.media_search_result import MediaSearchResult
from datetime import date, datetime



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
        self.cur = conn.cursor()

    def _row_to_movie(self, row: tuple) -> Movie:
        released_at = (
            date.fromisoformat(row[11])
            if row[11] is not None
            else None
        )

        created_at = (
            datetime.fromisoformat(row[19])
            if row[19] is not None
            else None
        )

        updated_at = (
            datetime.fromisoformat(row[20])
            if row[20] is not None
            else None
        )

        return Movie(
            id=row[0],
            imdb_id=row[1],
            media_type=row[2],
            title=row[3],
            year=row[4],
            genre=row[5],
            director=row[6],
            plot=row[7],
            poster=row[8],
            awards=row[9],
            runtime_minutes=row[10],
            released_at=released_at,
            imdb_rating=row[12],
            imdb_votes=row[13],
            metascore=row[14],
            box_office=row[15],
            budget=row[16],
            comment=row[17],
            avaliation=row[18],
            created_at=created_at,
            updated_at=updated_at,
            external_ratings=self._load_external_ratings(
                row[0]
            ),
        )

    def save_movie(self, movie: Movie) -> None:
        try:
            self.cur.execute(
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

            media_id = self.cur.lastrowid

            if media_id is None:
                raise RuntimeError(
                    "Não foi possível obter o ID da mídia."
                )

            self.cur.execute(
                """
                INSERT INTO movie_details (
                    media_id,
                    director
                )
                VALUES (?, ?)
                """,
                (
                    media_id,
                    movie.director,
                ),
            )

            for rating in movie.external_ratings:
                self.cur.execute(
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

                rating.media_id = media_id

            self.conn.commit()

            movie.id = media_id

        except Exception:
            self.conn.rollback()
            raise

    def _load_external_ratings(self, media_id: int,) -> list[ExternalRating]:
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

    def search_data_movie(self, title: str,) -> Movie | None:
            self.cur.execute(
                self._MOVIE_SELECT
                + """
                WHERE media.title = ? COLLATE NOCASE
                  AND media.media_type = 'movie'
                ORDER BY media.year DESC
                LIMIT 1
                """,
                (title,),
            )

            row = self.cur.fetchone()

            if row is None:
                return None

            return self._row_to_movie(row)

    def search_movie_by_id(self, movie_id: int,) -> Movie | None:
            self.cur.execute(
                self._MOVIE_SELECT
                + """
                WHERE media.id = ?
                  AND media.media_type = 'movie'
                """,
                (movie_id,),
            )

            row = self.cur.fetchone()

            if row is None:
                return None

            return self._row_to_movie(row)

    def search_movie_results(self, user_search: str,) -> list[MediaSearchResult]:
        
        pattern = f"%{user_search.strip()}%"

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
            WHERE title COLLATE NOCASE LIKE ?
              AND media_type = 'movie'
            ORDER BY
                title COLLATE NOCASE,
                year DESC
            """,
            (pattern,),
        ).fetchall()

        return [
            MediaSearchResult(
                local_id=row[0],
                imdb_id=row[1],
                title=row[2],
                year=(
                    str(row[3])
                    if row[3] is not None
                    else None
                ),
                media_type=row[4],
                poster=row[5],
            )
            for row in rows
        ]


    def list_movies(self) -> list[Movie]:
        self.cur.execute(
            self._MOVIE_SELECT
            + """
            WHERE media.media_type = 'movie'
            ORDER BY media.title COLLATE NOCASE
            """
        )

        rows = self.cur.fetchall()

        return [
            self._row_to_movie(row)
            for row in rows
        ]

    def delete_movie( self, movie_id: int,) -> bool:
        self.cur.execute(
            """
            DELETE FROM media
            WHERE id = ?
              AND media_type = 'movie'
            """,
            (movie_id,),
        )

        deleted = self.cur.rowcount > 0

        self.conn.commit()

        return deleted

    def update_review(self, user_review: int, movie_id: int,) -> bool:
        self.cur.execute(
            """
            UPDATE media
            SET avaliation = ?
            WHERE id = ?
              AND media_type = 'movie'
            """,
            (
                user_review,
                movie_id,
            ),
        )
        updated = self.cur.rowcount > 0
        self.conn.commit()
        return updated
    
    def update_comment(self, user_comment: str, movie_id: int,) -> bool:
        self.cur.execute(
            """
            UPDATE media
            SET comment = ?
            WHERE id = ?
              AND media_type = 'movie'
            """,
            (
                user_comment,
                movie_id,
            ),
        )

        updated = self.cur.rowcount > 0

        self.conn.commit()

        return updated
