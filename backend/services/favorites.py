from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.models import Book, Favorite, User
from schemas.cart_favorites import BookInList, FavoriteResponse, FavoritesResponse


def get_favorites(db: Session, user: User) -> FavoritesResponse:
    """Получить список избранного пользователя."""
    items = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    result = []
    for item in items:
        book = db.query(Book).filter(Book.id == item.book_id).first()
        if book:
            result.append(FavoriteResponse(
                id=item.id,
                book=BookInList.model_validate(book),
            ))
    return FavoritesResponse(items=result)


def add_to_favorites(db: Session, user: User, book_id: int) -> FavoriteResponse:
    """Добавить книгу в избранное."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

    existing = db.query(Favorite).filter(
        Favorite.user_id == user.id,
        Favorite.book_id == book_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Книга уже в избранном")

    fav = Favorite(user_id=user.id, book_id=book_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)

    return FavoriteResponse(id=fav.id, book=BookInList.model_validate(book))


def remove_from_favorites(db: Session, user: User, book_id: int) -> dict:
    """Убрать книгу из избранного."""
    fav = db.query(Favorite).filter(
        Favorite.user_id == user.id,
        Favorite.book_id == book_id,
    ).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Книга не найдена в избранном")

    db.delete(fav)
    db.commit()
    return {"message": "Книга убрана из избранного"}