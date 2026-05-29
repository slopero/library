from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.models import Book, CartItem, Purchase, User
from schemas.cart_favorites import BookInList, CartItemResponse, CartResponse


def get_cart(db: Session, user: User) -> CartResponse:
    """Получить корзину пользователя."""
    items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    result = []
    for item in items:
        book = db.query(Book).filter(Book.id == item.book_id).first()
        if book:
            result.append(CartItemResponse(
                id=item.id,
                book=BookInList.model_validate(book),
            ))
    total = sum(r.book.price for r in result)
    return CartResponse(items=result, total=total)


def add_to_cart(db: Session, user: User, book_id: int) -> CartItemResponse:
    """Добавить книгу в корзину."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

    # Проверяем что книга не куплена
    purchased = db.query(Purchase).filter(
        Purchase.user_id == user.id,
        Purchase.book_id == book_id,
    ).first()
    if purchased:
        raise HTTPException(status_code=400, detail="Книга уже куплена")

    # Проверяем что книга не в корзине уже
    existing = db.query(CartItem).filter(
        CartItem.user_id == user.id,
        CartItem.book_id == book_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Книга уже в корзине")

    item = CartItem(user_id=user.id, book_id=book_id)
    db.add(item)
    db.commit()
    db.refresh(item)

    return CartItemResponse(id=item.id, book=BookInList.model_validate(book))


def remove_from_cart(db: Session, user: User, item_id: int) -> dict:
    """Удалить книгу из корзины."""
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Позиция не найдена в корзине")

    db.delete(item)
    db.commit()
    return {"message": "Книга удалена из корзины"}


def checkout(db: Session, user: User) -> dict:
    """Оформить покупку — перенести все книги из корзины в купленные."""
    items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    if not items:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    total = Decimal("0")
    for item in items:
        book = db.query(Book).filter(Book.id == item.book_id).first()
        if book:
            from models.models import Purchase
            purchase = Purchase(
                user_id=user.id,
                book_id=item.book_id,
                price_paid=book.price,
            )
            db.add(purchase)
            total += book.price
        db.delete(item)

    db.commit()
    return {"message": "Покупка оформлена", "total": str(total)}