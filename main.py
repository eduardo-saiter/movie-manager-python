from utils.exhibition import (
    menu,
    show_movie
)

from services.movie_services import MovieServices
from clients.movie_api_client import MovieApiClient
from repositories.movies_repository import MovieRepository
from database.database import (
    connect,
    initialize_database
)

import requests

import sqlite3



def main() -> None:
    conn = connect()
    try:

        initialize_database(conn)

        api_client = MovieApiClient()
        repository = MovieRepository(conn)
        service = MovieServices(api_client,repository)

        while True:

            menu()

            option = input("> ")

            try:

                if option == "1":
                    print("\nQual é o nome do filme?")
                    user_search = input("> ").strip()

                    try:
                        movie = service.search_movie(user_search)
                        if movie.id is None:
                            print("\nProcurando título na internet...")
                            print("Resultado da busca: ")
                            service.details_movie(movie)
                            service.save_movie(movie)

                        else:
                            print("Resultado da busca: ")
                            service.details_movie(movie)
                        
                    except (ValueError,ConnectionError) as e:
                        print(f"\n{e}")


                elif option == "2":
                    service.list_saved_movies()

                elif option == "3":
                    try:
                        print("\nQual o nome do filme?")
                        user_search = input("> ")
                        movie = service.search_movie(user_search)
                        if movie is not None:
                            print("\nDigite sua nova review (0-5):")
                            user_review = input(">")
                            service.new_review_movie(user_review,movie)
                    except ValueError as e:
                        print(e)
                elif option == "4":
                    try:
                        print("\nQual o nome do filme?")
                        user_search = input("> ")
                        movie = service.search_movie(user_search)
                        if movie is not None:
                            print("\nDigite seu novo comentário:")
                            user_comment = input(">")
                            service.new_comment_movie(user_comment,movie)
                    except ValueError as e:
                        print(e)

                elif option == "5":
                    try:
                        print("\nQual o nome do filme?")
                        user_search = input("> ")
                        service.delete_saved_movie(user_search)
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