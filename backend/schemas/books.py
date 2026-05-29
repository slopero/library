from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BookCard(BaseModel):
    """Данные книги для отображения карточки на главной странице."""
    id: int
    title: str
    authors: str
    genre: str
    year: int
    language: str
    price: Decimal

    model_config = {"from_attributes": True}


class BookCreate(BaseModel):
    """Данные для создания новой книги — приходят от администратора."""
    title: str
    authors: str
    genre: str
    year: int
    language: str
    price: Decimal
    description: str | None = None


class BookListResponse(BaseModel):
    """Ответ сервера на запрос списка книг."""
    items: list[BookCard]
    total: int
    page: int
    pages: int


class ReviewCard(BaseModel):
    """Отзыв для отображения на странице книги."""
    id: int
    user_id: int
    text: str
    rating: int
    created_at: str

    model_config = {"from_attributes": True}


class BookDetail(BaseModel):
    """Полные данные книги для страницы книги."""
    id: int
    title: str
    authors: str
    genre: str
    year: int
    language: str
    price: Decimal
    description: str | None
    text_path: str | None = None
    reviews: list[ReviewCard] = []
    avg_rating: float | None = None

    model_config = {"from_attributes": True}