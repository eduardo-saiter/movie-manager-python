from utils.exhibition import (
    menu,
    show_movie
)

from services.movie_services import MovieServices
from clients.movie_api_client import MovieApiClient
import requests
import sqlite3

def main() -> None:
    try:

        api_client = MovieApiClient()
        service = MovieServices(api_client)

        while True:

            menu()

            option = input("> ")

            try:

                if option == "1":

                    user_search = input("> ").strip()

                    try:
                        movie = service.search_movie(user_search)
                        print("Resultado da busca: ")
                        show_movie(movie)
                        
                    except (ValueError,ConnectionError) as e:
                        print(f"\n{e}")

                elif option == "2":
                    print("Saindo do sistema...")
                    break
                
                else:
                    print("Opção Inválida")

            except sqlite3.Error as error:
                    print("Erro ao acessar o banco de dados.")
                    print(f"Detalhes: {error}")


    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")


if __name__ == '__main__':
    main()