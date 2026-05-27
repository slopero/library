from decimal import Decimal
from pydantic import BaseModel


class BookCreate(BaseModel):
    """Данные для создания новой книги — приходят от администратора."""
    title:       str
    authors:     str
    genre:       str
    year:        int
    language:    str
    price:       Decimal
    description: str | None = None  # необязательное поле


class BookCreateResponse(BaseModel):
    """Ответ после успешного создания книги."""
    id:      int
    title:   str
    message: str = "Книга успешно добавлена"

    model_config = {"from_attributes": True}