from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from data.database import get_db
from services.dependencies import get_current_admin
from models.models import Administrator
from schemas.books import BookListResponse
from schemas.books_admin import BookCreate, BookCreateResponse
from services.books import get_books
from services.books_admin import create_book, delete_book

router = APIRouter(prefix="/books", tags=["books"])


# ── Публичные эндпоинты (доступны всем) ──────

@router.get("/", response_model=BookListResponse)
def list_books(
    page:      int      = Query(default=1, ge=1),
    search:    str|None = Query(default=None),
    genre:     str|None = Query(default=None),
    language:  str|None = Query(default=None),
    year_from: int|None = Query(default=None, ge=0),
    year_to:   int|None = Query(default=None, ge=0),
    sort:      str      = Query(default="title", pattern="^(title|author|year)$"),
    db: Session = Depends(get_db),
) -> BookListResponse:
    """Получить список книг с фильтрацией, поиском и пагинацией."""
    return get_books(
        db=db, page=page, search=search, genre=genre,
        language=language, year_from=year_from, year_to=year_to, sort=sort,
    )


# ── Эндпоинты только для администратора ──────

@router.post("/", response_model=BookCreateResponse)
def add_book(
    data:  BookCreate = ...,
    db:    Session    = Depends(get_db),
    admin: Administrator = Depends(get_current_admin),
) -> BookCreateResponse:
    """Добавить новую книгу. Только для администраторов."""
    return create_book(db, data, admin)


@router.delete("/{book_id}")
def remove_book(
    book_id: int,
    db:      Session = Depends(get_db),
    admin:   Administrator = Depends(get_current_admin),
) -> dict:
    """Удалить книгу по id. Только для администраторов."""
    return delete_book(db, book_id, admin)