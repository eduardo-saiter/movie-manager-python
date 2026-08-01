
def menu() -> None:
    print("\n=== Movie Manager ===")
    print("1. Search movie")
    print("2. List Saved Movies")
    print("3. Update Movie Review")
    print("4. Update Movie Comment")
    print("5. Delete Movie")
    print("6. Exit")


def show_movie(movie) -> None:
    print(f"Título: {movie.title}")
    print(f"Ano: {movie.year}")
    print(f"Gênero: {movie.genre}")
    print(f"Diretor: {movie.director}")
    if movie.avaliation is not None:
        stars = (
            "⭐" * movie.avaliation
            + "☆" * (5 - movie.avaliation))
        print(f"Avaliação: {stars} ({movie.avaliation}/5)")
    if movie.comment is not None:
        print(f"Comentário: {movie.comment}")
