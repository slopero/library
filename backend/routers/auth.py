from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
 
from data.database import get_db
from services.dependencies import get_current_admin, get_current_user
from models.models import Administrator, User
from schemas.admin_auth import AdminAuthResponse, AdminLogin, AdminRegister
from schemas.user_auth import UserAuthResponse, UserLogin, UserRegister
from services.auth_admin import login_admin, register_admin
from services.auth_user import login_user, register_user


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

@user_router.get("/me")
def user_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "birth_date": str(current_user.birth_date),
    }

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

@admin_router.get("/me")
def admin_me(current_admin: Administrator = Depends(get_current_admin)):
    return {
        "id": current_admin.id,
        "full_name": current_admin.full_name,
        "position": current_admin.position,
        "birth_date": str(current_admin.birth_date),
    }