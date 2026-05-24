from pydantic import BaseModel


class AdminRegister(BaseModel):
    """Данные которые администратор вводит при регистрации."""
    full_name: str
    passport_series: str    # 4 цифры
    passport_number: str    # 6 цифр
    position: str
    birth_date: str         # формат "ДД.ММ.ГГГГ"
    appointed_at: str       # дата назначения на должность
    login: str
    password: str
    register_key: str       # секретный ключ @A7A9BE#


class AdminLogin(BaseModel):
    """Данные для входа администратора."""
    login: str
    password: str


class AdminCard(BaseModel):
    """Данные администратора которые возвращаем в ответе."""
    id: int
    full_name: str
    position: str

    model_config = {"from_attributes": True}


class AdminAuthResponse(BaseModel):
    """Ответ сервера на вход или регистрацию администратора."""
    success: bool
    token: str | None = None
    admin: AdminCard | None = None
    message: str | None = None