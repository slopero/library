from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.models import Administrator, Book, User
from schemas.books_admin import BookCreateResponse


def create_book(
    db: Session,
    user: User,
    title: str,
    authors: str,
    genre: str,
    year: int,
    language: str,
    price: float,
    description: str | None,
    text_path: str | None,
) -> BookCreateResponse:
    """Создать книгу. Привязываем к записи в administrators через user."""
    admin = db.query(Administrator).filter(Administrator.user_id == user.id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Запись администратора не найдена")

    book = Book(
        administrator_id=admin.id,
        title=title,
        authors=authors,
        genre=genre,
        year=year,
        language=language,
        price=price,
        description=description,
        text_path=text_path,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return BookCreateResponse(id=book.id, title=book.title)


def delete_book(db: Session, book_id: int, user: User) -> dict:
    """Удалить книгу по id."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")
    db.delete(book)
    db.commit()
    return {"message": f"Книга «{book.title}» удалена"}