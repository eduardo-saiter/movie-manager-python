import sqlite3

from clients.movie_api_client import MovieApiClient
from database.database import connect, initialize_database
from repositories.movies_repository import MovieRepository
from services.movie_services import MovieServices
from utils.exhibition import (
    menu,
    show_list_movies,
    show_movie,
)


def _require_movie_id(movie_id: int | None) -> int:
    if movie_id is None:
        raise ValueError("O filme não possui um ID válido.")

    return movie_id


def main() -> None:
    conn = connect()
    try:

        initialize_database(conn)

        api_client = MovieApiClient()
        repository = MovieRepository(conn)
        service = MovieServices(api_client, repository)

        while True:

            menu()

            option = input("> ")

            try:

                if option == "1":
                    print("\nQual é o nome do filme?")
                    user_search = input("> ").strip()

                    try:
                        print("Procurando filme localmente...")
                        movie = service.search_movie_by_title(user_search)
                        if movie is None:
                            print("Filme não encontrado no banco de dados.")
                            print("\nProcurando título na internet...")
                            movie = service.search_api_by_title(user_search)
                            print("Resultado da busca: ")
                            show_movie(movie)
                            print("\nDeseja salvar esse filme? (s/sim)")
                            conf_save = input("> ").strip()
                            if conf_save.lower() in ("s", "sim"):
                                print("\nDigite sua review? (0-5)")
                                user_review = input("> ")
                                try:
                                    review = int(user_review)
                                    if not 0 <= review <= 5:
                                        raise ValueError
                                    movie.avaliation = review
                                except ValueError:
                                    print(
                                        "Avaliação inválida. "
                                        "O filme será salvo com 0 estrelas."
                                    )

                                print("\nDigite seu comentário: ")
                                user_comment = input("> ")
                                if not user_comment:
                                    movie.comment = None
                                else:
                                    movie.comment = user_comment
                                service.save_movie(movie)
                        else:
                            print("Resultado da busca: ")
                            show_movie(movie)

                    except (ValueError, ConnectionError) as e:
                        print(f"\n{e}")

                elif option == "2":
                    try:
                        movies = service.list_saved_movies()
                        show_list_movies(movies)
                    except ValueError as e:
                        print(e)

                elif option == "3":
                    try:
                        print("\nQual o nome do filme?")
                        user_search = input("> ")
                        movie = service.search_movie_by_title(user_search)
                        if movie is not None:
                            print("\nDigite sua nova review (0-5):")
                            user_review = input("> ")
                            service.new_review_movie(
                                _require_movie_id(movie.id),
                                user_review,
                            )
                            print("Review adicionada com sucesso.")
                        else:
                            print("Filme não encontrado")
                    except ValueError as e:
                        print(e)
                elif option == "4":
                    try:
                        print("\nQual o nome do filme?")
                        user_search = input("> ")
                        movie = service.search_movie_by_title(user_search)
                        if movie is not None:
                            print("\nDigite seu novo comentário:")
                            user_comment = input("> ")
                            service.new_comment_movie(
                                _require_movie_id(movie.id),
                                user_comment,
                            )
                            print("Comentário adicionado com sucesso")
                        else:
                            print("Filme não encontrado")
                    except ValueError as e:
                        print(e)

                elif option == "5":
                    try:
                        print("\nQual o nome do filme?")
                        user_search = input("> ")
                        movie = service.search_movie_by_title(user_search)
                        if movie is not None:
                            print(f"\nDeseja excluir {movie.title} ? (s/sim)")
                            conf = input("> ").strip()
                            if conf.lower() in ("s", "sim"):
                                service.delete_saved_movie(
                                    _require_movie_id(movie.id)
                                )
                                print("O filme está sendo excluído...")
                                print("Puf, varrido da existência.")
                                print(
                                    f"O filme {movie.title} "
                                    "foi excluído com sucesso"
                                )
                        else:
                            print("Filme não encontrado")
                    except ValueError as e:
                        print(e)
                elif option == "6":
                    print("Saindo do sistema...")
                    break

                else:
                    print("Opção Inválida")

            except sqlite3.Error as error:
                print("Erro ao acessar o banco de dados.")
                print(f"Detalhes: {error}")

    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
