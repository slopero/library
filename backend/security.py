import hashlib
import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "library_idea_secret_key_2024")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password


def create_token(user_id: int, is_admin: bool) -> str:
    """Создать JWT токен. Всегда содержит user_id и is_admin."""
    payload = {
        "user_id":  user_id,
        "is_admin": is_admin,
        "exp":      datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None