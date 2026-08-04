from utils.exhibition import (
    menu,
    show_movie,
    show_list_movies,
)
from services.movie_services import MovieServices
from clients.movie_api_client import MovieApiClient
from repositories.movies_repository import MovieRepository
from database.database import (
    connect,
    initialize_database
)
import sqlite3
import time

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
                        print("Procurando filme localmente...")
                        time.sleep(1.5)
                        movie = service.search_movie(user_search)
                        if movie is None:
                            print("Filme não encontrado no banco de dados.")
                            print("\nProcurando título na internet...")
                            time.sleep(1.5)
                            movie = service.search_api(user_search)
                            print("Resultado da busca: ")
                            show_movie(movie)
                            print("\nDeseja salvar esse filme? (s/sim)")
                            conf_save = input("> ").strip()
                            if conf_save.lower() in ("s", "sim"):
                                print("\nDigite sua review? (0-5)")
                                user_review = input("> ")
                                if not user_review:
                                    print("O review não pode ser vazio.")
                                try:
                                    user_review = int(user_review)
                                    if user_review > 5 or user_review < 0:
                                        print("Review inválida.")
                                    else:
                                        movie.avaliation = user_review
                                except:
                                    print("Insira um número válido")
                    
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
                        
                    except (ValueError,ConnectionError) as e:
                        print(f"\n{e}")

                elif option == "2":
                    try:
                       movies = service.list_saved_movies()
                       show_list_movies(movies)
                    except ValueError as e:
                        print (e)

                elif option == "3":
                    try:
                        print("\nQual o nome do filme?")
                        user_search = input("> ")
                        movie = service.search_movie(user_search)
                        if movie is not None:
                            print("\nDigite sua nova review (0-5):")
                            user_review = input("> ")
                            service.new_review_movie(movie.id,user_review)
                            print("Review adicionada com sucesso.")
                        else:
                            print("Filme não encontrado")
                    except ValueError as e:
                        print(e)
                elif option == "4":
                    try:
                        print("\nQual o nome do filme?")
                        user_search = input("> ")
                        movie = service.search_movie(user_search)
                        if movie is not None:
                            print("\nDigite seu novo comentário:")
                            user_comment = input("> ")
                            service.new_comment_movie(movie.id,user_comment)
                            print("Comentário adicionado com sucesso")
                        else:
                            print("Filme não encontrado")
                    except ValueError as e:
                        print(e)

                elif option == "5":
                    try:
                        print("\nQual o nome do filme?")
                        user_search = input("> ")                  
                        movie = service.search_movie(user_search)
                        if movie is not None:
                            print(f"\nDeseja excluir {movie.title} ? (s/sim)")
                            conf = input("> ").strip()
                            if conf.lower() in ("s", "sim"):
                                print(movie.id)
                                id_movie = movie.id
                                service.delete_saved_movie(id_movie)
                                print("O filme está sendo excluído...")
                                time.sleep(1.5)
                                print("Puf, varrido da existência.")
                                print(f"O filme {movie.title} foi excluído com sucesso")
                        else:
                            print("Filme não encontrado")
                    except ValueError as e:
                        print (e)
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