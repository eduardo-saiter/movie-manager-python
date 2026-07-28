import sqlite3
from models.movie import Movie
from services.movie_services import MovieServices

class MovieRepository:

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.cur = conn.cursor()

    def save_movie(self,movie:Movie) -> None:
        self.cur.execute('''
        INSERT INTO movies (title, year, genre, director, plot) 
        VALUES (?,?,?,?,?)
        ''',(
            movie.title,
            movie.year,
            movie.genre,
            movie.director,
            movie.plot,
        )) 
        self.conn.commit()

