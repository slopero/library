from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from data.database import get_db
from schemas.user_auth import UserAuthResponse, UserLogin, UserRegister
from schemas.admin_auth import AdminAuthResponse, AdminLogin, AdminRegister
from services.auth_admin import register_admin, login_admin
from services.auth_user import register_user, login_user


user_router = APIRouter(prefix="/auth/user", tags=["auth-user"])
admin_router = APIRouter(prefix="/auth/admin", tags=["auth-admin"])

@user_router.post("/register", response_model=UserAuthResponse)
def user_register(
    data: UserRegister,
    db: Session = Depends(get_db),
) -> UserAuthResponse:
    return register_user(db, data)


@user_router.post("/login", response_model=UserAuthResponse)
def user_login(
    data: UserLogin,
    db: Session = Depends(get_db),
) -> UserAuthResponse:
    return login_user(db, data)

@admin_router.post("/login", response_model=AdminAuthResponse)
def admin_login(
    data: AdminLogin,
    db: Session = Depends(get_db),
) -> AdminAuthResponse:
    return login_admin(db, data)

@admin_router.post("/register", response_model=AdminAuthResponse)
def admin_register(
    data: AdminRegister,
    db: Session = Depends(get_db),
) -> AdminAuthResponse:
    return register_admin(db, data)