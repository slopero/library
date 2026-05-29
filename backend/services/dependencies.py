from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from data.database import get_db
from models.models import User
from security import decode_token

bearer_scheme = HTTPBearer()


def _get_user_from_token(
    credentials: HTTPAuthorizationCredentials,
    db: Session,
) -> User:
    """Общая логика — достать пользователя из токена."""
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истёкший токен",
        )
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Любой авторизованный пользователь (включая админа).
    Используется для корзины, избранного, отзывов — функционал доступен всем.
    """
    return _get_user_from_token(credentials, db)


def get_current_regular_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Только обычный пользователь (не админ).
    Используется там где нужно явно исключить администратора.
    """
    user = _get_user_from_token(credentials, db)
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )
    return user


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Только администратор.
    Используется для управления книгами и других админских действий.
    Возвращает объект User с is_admin=True.
    """
    user = _get_user_from_token(credentials, db)
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )
    return user