import sqlite3
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from services.movie_services import MovieServices
from web_dependencies import get_movie_service, templates

router = APIRouter()

@router.get("/")
def home(request: Request, service: MovieServices = Depends(get_movie_service)):
    try:
        movies = service.list_saved_movies()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": "Movie Manager",
                "movies": movies
            },
        )
    except (ValueError,sqlite3.Error) as error:
            status_code = (503
            if isinstance(error, sqlite3.Error)
            else 400)

            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "title": "Movie Manager",
                    "movies": [],
                    "error": str(error),
                },
                status_code=status_code
            )


@router.get("/search")
def search_movie_page(
    request: Request,
    title: str,
    service: MovieServices = Depends(get_movie_service)
):
    try:
        movie = service.search_movie(title)

        if movie is None:
            movie = service.search_api(title)


        return templates.TemplateResponse(
            request=request,
            name="search_result.html",
            context={
                "page_title": "Resultado da pesquisa",
                "movie": movie,
                "error": None,
            },
        )
        
    except (ValueError, ConnectionError, sqlite3.Error) as error:
        status_code = (
            503
            if isinstance(error, (ConnectionError, sqlite3.Error))
            else 400
        )
        error_message = (
            "Não foi possível acessar o banco de dados."
            if isinstance(error, sqlite3.Error)
            else str(error)
        )

        return templates.TemplateResponse(
            request=request,
            name="search_result.html",
            context={
                "page_title": "Resultado da pesquisa",
                "movie": None,
                "error": error_message,
            },
            status_code=status_code,
        )


@router.post("/movies/save")
def save_movie_page(
    request: Request,
    title: str = Form(...),
    service: MovieServices = Depends(get_movie_service)
):
    try:
        saved_movie = service.search_movie(title)

        if saved_movie is None:
                movie = service.search_api(title)
                service.save_movie(movie)

        query = urlencode({"title": title})

        return RedirectResponse(
            url=f"/search?{query}",
            status_code=303,
        )
    
    except (ValueError, ConnectionError) as error:
        status_code = (
            503
            if isinstance(error, ConnectionError)
            else 400
        )

        return templates.TemplateResponse(
            request=request,
            name="search_result.html",
            context={
                "page_title": "Resultado da pesquisa",
                "movie": None,
                "error": str(error),
            },
            status_code=status_code,
        )
    
@router.post("/movies/{movie_id}/update-rating")
def update_rating_page(
    request: Request,
    movie_id: int,
    rating: int = Form(...),
    title: str = Form(...),
    service: MovieServices = Depends(get_movie_service)
):
    try:
        service.new_review_movie(movie_id, rating)

    except (ValueError,ConnectionError) as error:
        status_code = (503
        if isinstance(error, ConnectionError)
        else 400)
        movie = service.search_movie_by_id(movie_id)

        return templates.TemplateResponse(
            request=request,
            name="search_result.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": movie,
                "error": str(error),
                },
            status_code=status_code,
        )
    
    query = urlencode({"title": title})

    return RedirectResponse(
        url=f"/search?{query}",
        status_code=303,

    )


@router.post("/movies/{movie_id}/update-comment")
def update_comment_page(
    request: Request,
    movie_id: int,
    comment: str = Form(...),
    title: str = Form(...),
    service: MovieServices = Depends(get_movie_service)
):
    try:
        service.new_comment_movie(movie_id, comment)
    except (ValueError,ConnectionError) as error:
        status_code = (503
        if isinstance(error, ConnectionError)
        else 400)
        movie = service.search_movie_by_id(movie_id)

        return templates.TemplateResponse(
            request=request,
            name="search_result.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": movie,
                "error": str(error),
                },
            status_code=status_code,
        )
        
    query = urlencode({"title": title})

    return RedirectResponse(
        url=f"/search?{query}",
        status_code=303,
    )


@router.post("/movies/{movie_id}/delete-movie", name="delete_movie_page")
def delete_movie_page(
    request: Request,
    movie_id: int,
    service: MovieServices = Depends(get_movie_service)
):
    try:
        service.delete_saved_movie(movie_id)

    except (ValueError,ConnectionError) as error:
            status_code = (503
                if isinstance(error, ConnectionError)
                else 400)
            return templates.TemplateResponse(
                request=request,
                name="search_result.html",
                context={
                    "page_title": "Resultado da pesquisa",
                    "movie": None,
                    "error": str(error),
                },
                status_code=status_code
            )

    return RedirectResponse(
        url="/",
        status_code=303,
    )

@router.get("/movies/{movie_id}", name="search_movie_id_page")
def movie_details_page(
    request: Request,
    movie_id: int,
    service: MovieServices = Depends(get_movie_service)
):
    movie = service.search_movie_by_id(movie_id)

    if movie is None:
        return templates.TemplateResponse(
            request=request,
            name="search_result.html",
            context={
                "page_title": "Filme não encontrado",
                "movie": None,
                "error": "O filme solicitado não foi encontrado.",
            },
            status_code=404,
        )
    
    return templates.TemplateResponse(
        request=request,
        name="search_result.html",
        context={"movie": movie, "page_title": "Detalhes do filme"},
    )