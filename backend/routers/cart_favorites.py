from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from data.database import get_db
from services.dependencies import get_current_user
from models.models import User
from schemas.cart_favorites import (
    CartItemAdd, CartItemResponse, CartResponse,
    FavoriteAdd, FavoriteResponse, FavoritesResponse,
)
from services.cart import add_to_cart, checkout, get_cart, remove_from_cart
from services.favorites import add_to_favorites, get_favorites, remove_from_favorites

cart_router      = APIRouter(prefix="/cart",      tags=["cart"])
favorites_router = APIRouter(prefix="/favorites", tags=["favorites"])


# ── Корзина ───────────────────────────────────

@cart_router.get("/", response_model=CartResponse)
def get_user_cart(
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
) -> CartResponse:
    """Получить содержимое корзины."""
    return get_cart(db, user)


@cart_router.post("/", response_model=CartItemResponse)
def add_book_to_cart(
    data: CartItemAdd,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
) -> CartItemResponse:
    """Добавить книгу в корзину."""
    return add_to_cart(db, user, data.book_id)


@cart_router.delete("/{item_id}")
def remove_book_from_cart(
    item_id: int,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
) -> dict:
    """Удалить позицию из корзины."""
    return remove_from_cart(db, user, item_id)


@cart_router.post("/checkout")
def checkout_cart(
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
) -> dict:
    """Оформить покупку — все книги из корзины становятся купленными."""
    return checkout(db, user)


# ── Избранное ─────────────────────────────────

@favorites_router.get("/", response_model=FavoritesResponse)
def get_user_favorites(
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
) -> FavoritesResponse:
    """Получить список избранного."""
    return get_favorites(db, user)


@favorites_router.post("/", response_model=FavoriteResponse)
def add_book_to_favorites(
    data: FavoriteAdd,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
) -> FavoriteResponse:
    """Добавить книгу в избранное."""
    return add_to_favorites(db, user, data.book_id)


@favorites_router.delete("/{book_id}")
def remove_book_from_favorites(
    book_id: int,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
) -> dict:
    """Убрать книгу из избранного."""
    return remove_from_favorites(db, user, book_id)


# ── Купленные книги ───────────────────────────

from models.models import Purchase, Book
from decimal import Decimal

purchases_router = APIRouter(prefix="/purchases", tags=["purchases"])

@purchases_router.get("/")
def get_purchases(
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
) -> dict:
    """Получить список купленных книг."""
    purchases = db.query(Purchase).filter(Purchase.user_id == user.id).all()
    result = []
    for p in purchases:
        book = db.query(Book).filter(Book.id == p.book_id).first()
        if book:
            result.append({
                "id":           p.id,
                "purchased_at": str(p.purchased_at.date()),
                "price_paid":   str(p.price_paid),
                "book": {
                    "id":      book.id,
                    "title":   book.title,
                    "authors": book.authors,
                    "price":   str(book.price),
                }
            })
    return {"items": result}