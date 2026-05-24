from datetime import date

from sqlalchemy.orm import Session

from models.models import User, UserAuth
from schemas.user_auth import UserAuthResponse, UserCard, UserLogin, UserRegister
from security import create_token, hash_password, verify_password

def register_user(db: Session, data: UserRegister) -> UserAuthResponse:
    """Регистрация нового пользователя"""

    # Проверка занят ли логин 
    existing = db.query(UserAuth).filter(UserAuth.login == data.login).first()
    if existing:
        return UserAuthResponse(success=False, message="Логин уже занят")
    # Преобразуем строку даты в объект date
    try:
        day, month, year = data.birth_date.split(".")
        birth_date = date(int(year), int(month), int(day))
    except (ValueError, AttributeError):
        return UserAuthResponse(success=False, message="Неверный формат даты")
    
    user = User(
        full_name = data.full_name,
        email = data.email,
        birth_date = birth_date
    )

    db.add(user)
    db.flush()  # Получаем id пользователя до коммита

    user_auth = UserAuth(
        user_id = user.id,
        login = data.login,
        password_hash = hash_password(data.password)
    )
    db.add(user_auth)

    db.commit()
    db.refresh(user)

    token = create_token({"user_id": user.id, "is_admin": False})

    return UserAuthResponse(
        success=True,
        token=token,
        user=UserCard.model_validate(user)
    )

def login_user(db: Session, data: UserLogin) -> UserAuthResponse:
    """Авторизация пользователя"""

    auth = db.query(UserAuth).filter(UserAuth.login == data.login).first()
    if not auth or not verify_password(data.password, auth.password_hash):
        return UserAuthResponse(success=False, message="Неверный логин или пароль")
    
    user = db.query(User).filter(
        User.id == auth.user_id
    ).first()

    token = create_token({"user_id": user.id, "is_admin": False})

    return UserAuthResponse(
        success=True,
        token=token,
        user=UserCard.model_validate(user)
    )