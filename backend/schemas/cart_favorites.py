from decimal import Decimal
from pydantic import BaseModel


class BookInList(BaseModel):
    """Краткая информация о книге для корзины и избранного."""
    id:      int
    title:   str
    authors: str
    price:   Decimal

    model_config = {"from_attributes": True}


# ── Корзина ───────────────────────────────────

class CartItemAdd(BaseModel):
    book_id: int


class CartItemResponse(BaseModel):
    id:      int
    book:    BookInList

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total: Decimal   # итоговая сумма


# ── Избранное ─────────────────────────────────

class FavoriteAdd(BaseModel):
    book_id: int


class FavoriteResponse(BaseModel):
    id:   int
    book: BookInList

    model_config = {"from_attributes": True}


class FavoritesResponse(BaseModel):
    items: list[FavoriteResponse]