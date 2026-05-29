from datetime import date

from sqlalchemy.orm import Session

from models.models import User, UserAuth
from schemas.user_auth import UserAuthResponse, UserCard, UserLogin, UserRegister
from security import create_token, hash_password, verify_password


def register_user(db: Session, data: UserRegister) -> UserAuthResponse:
    """Регистрация нового пользователя."""
    existing_login = db.query(UserAuth).filter(UserAuth.login == data.login).first()
    if existing_login:
        return UserAuthResponse(success=False, message="Логин уже занят")

    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        return UserAuthResponse(success=False, message="Email уже зарегистрирован")

    try:
        day, month, year = data.birth_date.split(".")
        birth_date = date(int(year), int(month), int(day))
    except (ValueError, AttributeError):
        return UserAuthResponse(success=False, message="Неверный формат даты")

    user = User(
        full_name=data.full_name,
        email=data.email,
        birth_date=birth_date,
        is_admin=False,
    )
    db.add(user)
    db.flush()

    user_auth = UserAuth(
        user_id=user.id,
        login=data.login,
        password_hash=hash_password(data.password),
    )
    db.add(user_auth)
    db.commit()
    db.refresh(user)

    token = create_token(user_id=user.id, is_admin=False)
    return UserAuthResponse(success=True, token=token, user=UserCard.model_validate(user))


def login_user(db: Session, data: UserLogin) -> UserAuthResponse:
    """Вход — работает для пользователей и администраторов."""
    user_auth = db.query(UserAuth).filter(UserAuth.login == data.login).first()

    if not user_auth or not verify_password(data.password, user_auth.password_hash):
        return UserAuthResponse(success=False, message="Неверный логин или пароль")

    user = db.query(User).filter(User.id == user_auth.user_id).first()
    token = create_token(user_id=user.id, is_admin=user.is_admin)

    return UserAuthResponse(
        success=True,
        token=token,
        user=UserCard.model_validate(user),
        is_admin=user.is_admin,
    )