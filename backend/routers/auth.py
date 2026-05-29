from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from data.database import get_db
from services.dependencies import get_current_admin, get_current_user
from models.models import User
from schemas.user_auth import UserAuthResponse, UserLogin, UserRegister
from services.auth_user import login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserAuthResponse)
def register(data: UserRegister, db: Session = Depends(get_db)) -> UserAuthResponse:
    """Регистрация нового пользователя."""
    return register_user(db, data)


@router.post("/login", response_model=UserAuthResponse)
def login(data: UserLogin, db: Session = Depends(get_db)) -> UserAuthResponse:
    """Вход для пользователей и администраторов — один эндпоинт."""
    return login_user(db, data)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    """Получить данные текущего авторизованного пользователя."""
    result = {
        "id":            user.id,
        "full_name":     user.full_name,
        "email":         user.email,
        "birth_date":    str(user.birth_date),
        "registered_at": str(user.registered_at.date()),
        "is_admin":      user.is_admin,
    }
    # Если администратор — добавляем рабочие данные
    if user.is_admin and user.administrator:
        result["position"]     = user.administrator.position
        result["appointed_at"] = str(user.administrator.appointed_at)
    return result