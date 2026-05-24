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


class BookListResponse(BaseModel):
    """Ответ сервера на запрос списка книг."""
    items: list[BookCard] 
    total: int              
    page: int               
    pages: int              