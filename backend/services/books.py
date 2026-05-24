import math

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.models import Book
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

    # Если клиент передал неизвестный sort — используем title по умолчанию
    order_column = sort_options.get(sort, Book.title)
    query = query.order_by(order_column)

    # ── Пагинация ────────────────────────────────────────────────────────────

    # Сначала считаем сколько всего записей найдено (до обрезки страницей).
    # func.count() — это SQL COUNT(), считает количество строк.
    total = query.with_entities(func.count()).scalar()

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