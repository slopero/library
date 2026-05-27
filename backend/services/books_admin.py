from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.models import Administrator, Book
from schemas.books_admin import BookCreate, BookCreateResponse


def create_book(
    db: Session,
    data: BookCreate,
    admin: Administrator,
) -> BookCreateResponse:
    """Создать новую книгу. Привязывает книгу к администратору который её добавил."""

    book = Book(
        administrator_id=admin.id,
        title=data.title,
        authors=data.authors,
        genre=data.genre,
        year=data.year,
        language=data.language,
        price=data.price,
        description=data.description,
    )
    db.add(book)
    db.commit()
    db.refresh(book)

    return BookCreateResponse(id=book.id, title=book.title)


def delete_book(db: Session, book_id: int, admin: Administrator) -> dict:
    """Удалить книгу по id.

    Проверяем что книга существует — если нет, возвращаем 404.
    Любой администратор может удалить любую книгу.
    """
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена",
        )

    db.delete(book)
    db.commit()

    return {"message": f"Книга «{book.title}» удалена"}