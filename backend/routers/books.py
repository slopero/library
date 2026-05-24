from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from data.database import get_db
from schemas.books import BookListResponse
from services.books import get_books

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=BookListResponse)
def list_books(
    # Query() — говорит FastAPI что этот параметр берётся из строки запроса.
    # Например: GET /books/?search=толстой&page=2&sort=title
    page: int = Query(default=1, ge=1, description="Номер страницы"),

    search: str | None = Query(default=None, description="Поиск по названию и автору"),
    genre: str | None = Query(default=None, description="Фильтр по жанру"),
    language: str | None = Query(default=None, description="Фильтр по языку"),
    year_from: int | None = Query(default=None, ge=0, description="Год издания от"),
    year_to: int | None = Query(default=None, ge=0, description="Год издания до"),

    # Literal ограничивает допустимые значения прямо в документации API.
    # FastAPI вернёт ошибку если передать что-то кроме этих трёх значений.
    sort: str = Query(default="title", pattern="^(title|author|year)$", description="Сортировка"),

    # Depends(get_db) — FastAPI автоматически создаст сессию базы данных
    # и передаст её сюда. После завершения запроса сессия закроется.
    db: Session = Depends(get_db),
) -> BookListResponse:
    return get_books(
        db=db,
        page=page,
        search=search,
        genre=genre,
        language=language,
        year_from=year_from,
        year_to=year_to,
        sort=sort,
    )