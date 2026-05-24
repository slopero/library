from datetime import date

from sqlalchemy.orm import Session

from models.models import Administrator, AdminAuth
from schemas.admin_auth import AdminAuthResponse, AdminCard, AdminLogin, AdminRegister
from security import create_token, hash_password, verify_admin_key, verify_password


def register_admin(db: Session, data: AdminRegister) -> AdminAuthResponse:
    """Зарегистрировать нового администратора."""

    # Первым делом проверяем секретный ключ
    if not verify_admin_key(data.register_key):
        return AdminAuthResponse(success=False, message="Неверный ключ регистрации")

    # Проверяем что логин не занят
    existing = db.query(AdminAuth).filter(AdminAuth.login == data.login).first()
    if existing:
        return AdminAuthResponse(success=False, message="Логин уже занят")

    # Преобразуем строки дат в объекты date
    try:
        day, month, year = data.birth_date.split(".")
        birth_date = date(int(year), int(month), int(day))

        day, month, year = data.appointed_at.split(".")
        appointed_at = date(int(year), int(month), int(day))
    except (ValueError, AttributeError):
        return AdminAuthResponse(success=False, message="Неверный формат даты")

    # Создаём запись администратора
    admin = Administrator(
        full_name=data.full_name,
        passport_series=data.passport_series,
        passport_number=data.passport_number,
        position=data.position,
        birth_date=birth_date,
        appointed_at=appointed_at,
    )
    db.add(admin)
    db.flush()

    # Создаём запись авторизации
    admin_auth = AdminAuth(
        administrator_id=admin.id,
        login=data.login,
        password_hash=hash_password(data.password),
    )
    db.add(admin_auth)

    db.commit()
    db.refresh(admin)

    # В токен кладём is_admin=True — по этому флагу бэк будет
    # понимать что запрос делает администратор, а не обычный пользователь
    token = create_token({"admin_id": admin.id, "is_admin": True})

    return AdminAuthResponse(
        success=True,
        token=token,
        admin=AdminCard.model_validate(admin),
    )


def login_admin(db: Session, data: AdminLogin) -> AdminAuthResponse:
    """Войти как администратор."""

    admin_auth = db.query(AdminAuth).filter(AdminAuth.login == data.login).first()

    if not admin_auth or not verify_password(data.password, admin_auth.password_hash):
        return AdminAuthResponse(success=False, message="Неверный логин или пароль")

    admin = db.query(Administrator).filter(
        Administrator.id == admin_auth.administrator_id
    ).first()

    token = create_token({"admin_id": admin.id, "is_admin": True})

    return AdminAuthResponse(
        success=True,
        token=token,
        admin=AdminCard.model_validate(admin),
    )