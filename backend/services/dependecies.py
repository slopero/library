from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from data.database import get_db
from models import Administrator, User
from security import decode_token

# HTTPBearer — говорит FastAPI что ожидаем токен в заголовке:
# Authorization: Bearer <токен>
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Зависимость для защищённых роутеров пользователя.

    Проверяет токен и возвращает объект пользователя из базы.
    Если токен неверный — возвращает 401.
    """
    
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("is_admin"):
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


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Administrator:
    """Зависимость для защищённых роутеров администратора.

    Проверяет токен и возвращает объект администратора из базы.
    Если токен неверный или это не админ — возвращает 401.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or not payload.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недостаточно прав",
        )

    admin = db.query(Administrator).filter(
        Administrator.id == payload.get("admin_id")
    ).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Администратор не найден",
        )

    return admin