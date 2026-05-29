from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    full_name:  str
    email:      EmailStr
    birth_date: str
    login:      str
    password:   str


class UserLogin(BaseModel):
    login:    str
    password: str


class UserCard(BaseModel):
    id:        int
    full_name: str
    email:     str
    is_admin:  bool = False

    model_config = {"from_attributes": True}


class UserAuthResponse(BaseModel):
    success:  bool
    token:    str | None = None
    user:     UserCard | None = None
    is_admin: bool = False
    message:  str | None = None