import hashlib
import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "library_idea_secret_key_2024")

# Алгоритм подписи токена
ALGORITHM = "HS256"

# Время жизни токена — 24 часа.
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Ключ для регистрации администратора
# 10998238 в hex = a7a9be
ADMIN_REGISTER_KEY = "@A7A9BE#"


# Работа с паролями (SHA-256)
def hash_password(password: str) -> str:
    """Хэшировать пароль через SHA-256. Возвращает строку из 64 символов"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить что введённый пароль соответствует хэшу из базы."""
    return hash_password(plain_password) == hashed_password


# Работа с JWT токенами
def create_token(data: dict) -> str:
    """Создать JWT токен.
    data — словарь с данными которые будут внутри токена.
    Автоматически добавляет поле "exp" — время истечения токена.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload["exp"] = expire

    # jwt.encode — создаёт токен, подписывает его SECRET_KEY
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Декодировать и проверить JWT токен.

    Возвращает словарь с данными если токен валидный,
    или None если токен неверный или истёк.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # JWTError покрывает все случаи: неверная подпись, истёкший токен и т.д.
        return None


def verify_admin_key(key: str) -> bool:
    """Проверить ключ регистрации администратора."""
    return key == ADMIN_REGISTER_KEY