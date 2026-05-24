import re
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship, validates


# DeclarativeBase — это базовый класс от SQLAlchemy.
# Все наши модели будут наследоваться от Base,
# чтобы SQLAlchemy знал что это таблицы базы данных.
class Base(DeclarativeBase):
    pass



#  Вспомогательная функция для проверки "только буквы и пробелы"
def only_letters(value: str, field_name: str) -> str:
    """Проверяет что строка содержит только буквы (рус/лат) и пробелы."""
    if value and not re.fullmatch(r"[А-Яа-яЁёA-Za-z\s\-]+", value):
        raise ValueError(f"Поле '{field_name}' должно содержать только буквы")
    return value



#  Администратор
class Administrator(Base):
    __tablename__ = "administrators"

    
    id = Column(Integer, primary_key=True, autoincrement=True)

    full_name        = Column(String(150), nullable=False)
    passport_series  = Column(String(4),   nullable=False)   # ровно 4 цифры
    passport_number  = Column(String(6),   nullable=False)   # ровно 6 цифр
    position         = Column(String(100), nullable=False)   # должность
    birth_date       = Column(Date,        nullable=False)
    appointed_at     = Column(Date,        nullable=False)   # дата назначения

    # CheckConstraint — ограничение на уровне БД:
    __table_args__ = (
        CheckConstraint(
            "passport_series ~ '^[0-9]{4}$'",
            name="ck_admin_passport_series"
        ),
        CheckConstraint(
            "passport_number ~ '^[0-9]{6}$'",
            name="ck_admin_passport_number"
        ),
    )

    # Связи (relationships) — удобный способ обращаться к связанным объектам.
    # Например: admin.books вернёт все книги добавленные этим администратором.
    auth      = relationship("AdminAuth", back_populates="administrator", uselist=False)
    books     = relationship("Book",      back_populates="administrator")

    # @validates — валидатор на уровне Python (до записи в БД)
    @validates("full_name", "position")
    def validate_letters_only(self, key, value):
        return only_letters(value, key)



#  Данные авторизации администратора
class AdminAuth(Base):
    __tablename__ = "admin_auth"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    # ForeignKey — ссылка на запись в другой таблице.
    # Если администратор удалён — его запись авторизации тоже удалится (CASCADE).
    administrator_id = Column(Integer, ForeignKey("administrators.id", ondelete="CASCADE"), nullable=False, unique=True)
    login            = Column(String(50),  nullable=False, unique=True)
    password_hash    = Column(String(64), nullable=False)  # храним хэш

    administrator = relationship("Administrator", back_populates="auth")



#  Пользователь
class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    full_name    = Column(String(150), nullable=False)
    email        = Column(String(150), nullable=False, unique=True)
    birth_date   = Column(Date,        nullable=False)
    registered_at = Column(DateTime,   nullable=False, default=lambda: datetime.now(timezone.utc))

    auth      = relationship("UserAuth",    back_populates="user", uselist=False)
    favorites = relationship("Favorite",    back_populates="user")
    purchases = relationship("Purchase",    back_populates="user")
    cart      = relationship("CartItem",    back_populates="user")
    reviews   = relationship("Review",      back_populates="user")

    @validates("full_name")
    def validate_letters_only(self, key, value):
        return only_letters(value, key)



#  Данные авторизации пользователя
class UserAuth(Base):
    __tablename__ = "user_auth"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    login         = Column(String(50),  nullable=False, unique=True)
    password_hash = Column(String(64), nullable=False)

    user = relationship("User", back_populates="auth")



#  Книга
class Book(Base):
    __tablename__ = "books"

    id               = Column(Integer,      primary_key=True, autoincrement=True)
    administrator_id = Column(Integer,      ForeignKey("administrators.id"), nullable=False)
    title            = Column(String(255),  nullable=False)
    authors          = Column(String(255),  nullable=False)  
    genre            = Column(String(100),  nullable=False)
    year             = Column(Integer,      nullable=False)
    description      = Column(Text,         nullable=True)
    language         = Column(String(50),   nullable=False)
    price            = Column(Numeric(10, 2), nullable=False)
    added_at         = Column(DateTime,     nullable=False, default=lambda: datetime.now(timezone.utc))

    administrator = relationship("Administrator", back_populates="books")
    reviews       = relationship("Review",    back_populates="book")
    favorites     = relationship("Favorite",  back_populates="book")
    purchases     = relationship("Purchase",  back_populates="book")
    cart_items    = relationship("CartItem",  back_populates="book")

    @validates("genre", "language")
    def validate_letters_only(self, key, value):
        return only_letters(value, key)



#  Отзыв
class Review(Base):
    __tablename__ = "reviews"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    book_id    = Column(Integer,     ForeignKey("books.id", ondelete="CASCADE"),  nullable=False)
    user_id    = Column(Integer,     ForeignKey("users.id", ondelete="CASCADE"),  nullable=False)
    created_at = Column(DateTime,    nullable=False, default=lambda: datetime.now(timezone.utc))
    text       = Column(String(1000), nullable=False)   # не более 1000 символов
    rating     = Column(Integer,     nullable=False)

    # Оценка только от 1 до 5
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating"),
    )

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")



#  Корзина
class CartItem(Base):
    __tablename__ = "cart"

    id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="cart")
    book = relationship("Book", back_populates="cart_items")



#  Избранное
class Favorite(Base):
    __tablename__ = "favorites"

    id         = Column(Integer,  primary_key=True, autoincrement=True)
    user_id    = Column(Integer,  ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id    = Column(Integer,  ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    added_at   = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="favorites")
    book = relationship("Book", back_populates="favorites")



#  Купленные книги
class Purchase(Base):
    __tablename__ = "purchases"

    id           = Column(Integer,       primary_key=True, autoincrement=True)
    user_id      = Column(Integer,       ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id      = Column(Integer,       ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    price_paid   = Column(Numeric(10, 2), nullable=False)
    purchased_at = Column(DateTime,      nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="purchases")
    book = relationship("Book", back_populates="purchases")