from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from data.database import get_db
from services.dependencies import get_current_admin, get_current_user
from models.models import Review, User
from schemas.books import BookDetail, BookListResponse
from schemas.books_admin import BookCreateResponse
from services.books import get_book_by_id, get_books, get_book_text_path
from services.books_admin import create_book, delete_book

router = APIRouter(prefix="/books", tags=["books"])


# ── Публичные эндпоинты ───────────────────────

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
    return get_books(
        db=db, page=page, search=search, genre=genre,
        language=language, year_from=year_from, year_to=year_to, sort=sort,
    )


@router.get("/{book_id}", response_model=BookDetail)
def get_book(book_id: int, db: Session = Depends(get_db)) -> BookDetail:
    """Получить одну книгу по id вместе с отзывами."""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")
    return book


@router.get("/{book_id}/text")
def get_book_text(
    book_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    text_path = get_book_text_path(db, book_id, user)

    backend_root = Path(__file__).resolve().parents[1]
    full_path = (backend_root / text_path).resolve()
    if not str(full_path).startswith(str(backend_root.resolve())):
        raise HTTPException(status_code=400, detail="Некорректный путь к файлу")

    if not full_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")

    return FileResponse(full_path, media_type="application/pdf", filename=full_path.name)


# ── Эндпоинты только для администратора ──────

@router.post("/", response_model=BookCreateResponse)
def add_book(
    title:       str = Form(...),
    authors:     str = Form(...),
    genre:       str = Form(...),
    year:        int = Form(...),
    language:    str = Form(...),
    price:       float = Form(...),
    description: str | None = Form(default=None),
    text_file:   UploadFile | None = File(default=None),
    db:    Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> BookCreateResponse:
    text_path: str | None = None
    if text_file:
        if text_file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Файл должен быть в формате PDF")

        target_dir = Path(__file__).resolve().parents[1] / "data" / "text"
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}.pdf"
        full_path = target_dir / filename
        with full_path.open("wb") as f:
            f.write(text_file.file.read())
        text_path = filename

    return create_book(
        db=db,
        user=admin,
        title=title,
        authors=authors,
        genre=genre,
        year=year,
        language=language,
        price=price,
        description=description,
        text_path=text_path,
    )


@router.delete("/{book_id}")
def remove_book(
    book_id: int,
    db:      Session = Depends(get_db),
    admin:   User = Depends(get_current_admin),
) -> dict:
    return delete_book(db, book_id, admin)


# ── Отзывы ────────────────────────────────────

@router.post("/{book_id}/reviews")
def add_review(
    book_id: int,
    text:    str,
    rating:  int,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
) -> dict:
    """Добавить отзыв к книге. Только для авторизованных пользователей."""
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Оценка должна быть от 1 до 5")
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Текст отзыва не более 1000 символов")

    # Проверяем что пользователь ещё не оставлял отзыв на эту книгу
    existing = db.query(Review).filter(
        Review.book_id == book_id,
        Review.user_id == user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже оставляли отзыв на эту книгу")

    review = Review(
        book_id=book_id,
        user_id=user.id,
        text=text,
        rating=rating,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "id":         review.id,
        "text":       review.text,
        "rating":     review.rating,
        "created_at": str(review.created_at.date()),
    }


@router.delete("/{book_id}/reviews/{review_id}")
def delete_review(
    book_id: int,
    review_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> dict:
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.book_id == book_id,
    ).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")

    db.delete(review)
    db.commit()
    return {"message": "Отзыв удалён"}