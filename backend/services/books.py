import math

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.models import Book, Purchase, User
from schemas.books import BookCard, BookListResponse

PAGE_SIZE = 20


def get_books(
    db: Session,
    page: int,
    search: str | None,
    genre: str | None,
    language: str | None,
    year_from: int | None,
    year_to: int | None,
    sort: str,
) -> BookListResponse:
    """Возвращает список книг с учётом фильтров, сортировки и пагинации."""

    # Начинаем строить запрос к базе.
    # query(Book) — говорим что хотим получить объекты типа Book.
    # Дальше будем добавлять фильтры через .filter()
    query = db.query(Book)

    # ── Фильтры ──────────────────────────────────────────────────────────────

    if search:
        # ilike — поиск по вхождению без учёта регистра.
        # % — спецсимвол SQL означает "любые символы".
        # Например ilike("%толст%") найдёт "Толстой" и "толстокожий".
        # | — это OR, ищем совпадение и в названии и в авторах.
        query = query.filter(
            Book.title.ilike(f"%{search}%") |
            Book.authors.ilike(f"%{search}%")
        )

    if genre:
        query = query.filter(Book.genre.ilike(f"%{genre}%"))

    if language:
        query = query.filter(Book.language.ilike(f"%{language}%"))

    if year_from:
        query = query.filter(Book.year >= year_from)

    if year_to:
        query = query.filter(Book.year <= year_to)

    # ── Сортировка ───────────────────────────────────────────────────────────

    # Словарь допустимых вариантов сортировки.
    # Это защита от того чтобы клиент не передал произвольное поле.
    sort_options = {
        "title":  Book.title,
        "author": Book.authors,
        "year":   Book.year,
    }

    total = query.count()
    # Если клиент передал неизвестный sort — используем title по умолчанию
    order_column = sort_options.get(sort, Book.title)
    query = query.order_by(order_column)

    # math.ceil — округление вверх. Если книг 21 и PAGE_SIZE=20,
    # то страниц будет 2, а не 1.
    pages = math.ceil(total / PAGE_SIZE) if total > 0 else 1

    # Приводим page к допустимому диапазону
    page = max(1, min(page, pages))

    # offset — пропустить первые N записей (для перехода на нужную страницу).
    # limit — взять не более PAGE_SIZE записей.
    # Например страница 2: offset=20, limit=20 → записи 21-40.
    books = query.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()

    return BookListResponse(
        items=[BookCard.model_validate(book) for book in books],
        total=total,
        page=page,
        pages=pages,
    )


def get_book_by_id(db: Session, book_id: int):
    """Получить одну книгу по id вместе с отзывами."""
    from models.models import Review
    from schemas.books import BookDetail, ReviewCard

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return None

    reviews = db.query(Review).filter(Review.book_id == book_id).order_by(Review.created_at.desc()).all()

    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    return BookDetail(
        id=book.id,
        title=book.title,
        authors=book.authors,
        genre=book.genre,
        year=book.year,
        language=book.language,
        price=book.price,
        description=book.description,
        avg_rating=avg_rating,
        reviews=[
            ReviewCard(
                id=r.id,
                user_id=r.user_id,
                text=r.text,
                rating=r.rating,
                created_at=str(r.created_at.date()),
            )
            for r in reviews
        ],
    )


def get_book_text_path(db: Session, book_id: int, user: User) -> str:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book or not book.text_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Текст книги не найден")

    text_path = book.text_path
    # Если в базе хранится только имя без папки/расширения — нормализуем.
    if "/" not in text_path and "\\" not in text_path:
        if not text_path.lower().endswith(".pdf"):
            text_path = f"{text_path}.pdf"
        text_path = f"data/text/{text_path}"

    if user.is_admin:
        return text_path

    purchase = db.query(Purchase).filter(
        Purchase.user_id == user.id,
        Purchase.book_id == book_id,
    ).first()
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ к тексту книги только для купленных книг",
        )

    return text_path