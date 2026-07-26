
def menu() -> None:
    print("\n=== Movie Manager ===")
    print("1. Search movie")
    print("2. Exit")

def show_movie(movie) -> None:
    print(movie.title)
    print(movie.year)
    print(movie.genre)
    print(movie.director)
    print(movie.plot)