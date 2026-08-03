import sqlite3
from models.movie import Movie


class MovieRepository:

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.cur = conn.cursor()

    def _row_to_movie(self, row: tuple) -> Movie:
        return Movie(
            title=row[0],
            year=row[1],
            genre=row[2],
            director=row[3],
            plot=row[4],
            comment=row[5],
            id=row[6],
            avaliation=row[7],
        )

    def save_movie(self, movie: Movie) -> Movie:
        self.cur.execute('''
        INSERT INTO movies (title, year, genre, director, plot, comment, avaliation) 
        VALUES (?,?,?,?,?,?,?)
        ''', (
            movie.title,
            movie.year,
            movie.genre,
            movie.director,
            movie.plot,
            movie.comment,
            movie.avaliation
        ))
        self.conn.commit()
        movie.id = self.cur.lastrowid
        return movie

    def search_data_movie(self, user_search:str) -> Movie | None:
        self.cur.execute('''
        SELECT title, year, genre, director, plot, comment, id, avaliation FROM movies WHERE title = ?
        ''',(user_search.strip().lower(),)
        )
        row = self.cur.fetchone()
        if row is None:
            return None
        return self._row_to_movie(row)

    def list_movies(self) -> list[Movie]:
        self.cur.execute(''' SELECT title, 
        year, 
        genre, 
        director,
        plot,
        comment, 
        id, 
        avaliation 
        FROM movies 
        ''')

        rows = self.cur.fetchall()
        return [self._row_to_movie(row) for row in rows]

    def delete_movie(self,id_movie: int) -> None:
        self.cur.execute('''
        DELETE FROM movies WHERE id = ?
        ''',(id_movie,))

        self.conn.commit()

    def update_review(self,user_review: int, id_movie: int) -> None:
        self.cur.execute('''
        UPDATE movies SET avaliation = ? WHERE id = ?
        ''',(user_review,id_movie))
        
        self.conn.commit()

    def update_comment(self,user_comment:str, id_movie: int) -> None:
        self.cur.execute('''
        UPDATE movies SET comment = ? WHERE id = ?
        ''',(user_comment,id_movie))

        self.conn.commit()
