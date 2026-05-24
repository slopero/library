from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """Данные которые пользователь вводит при регистрации."""
    full_name: str
    email: EmailStr      # EmailStr — Pydantic автоматически проверяет формат email
    birth_date: str      
    login: str
    password: str


class UserLogin(BaseModel):
    """Данные для входа."""
    login: str
    password: str


class UserCard(BaseModel):
    """Данные пользователя которые возвращаем в ответе."""
    id: int
    full_name: str
    email: str

    model_config = {"from_attributes": True}


class UserAuthResponse(BaseModel):
    """Ответ сервера на вход или регистрацию."""
    success: bool
    token: str | None = None
    user: UserCard | None = None
    message: str | None = None   # сообщение об ошибке если success=False