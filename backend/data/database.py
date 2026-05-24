import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base

# URL подключения к PostgreSQL собирается из переменных окружения.
# Это стандартная практика — пароли и хосты не пишутся прямо в коде,
# а берутся из окружения (или из .env файла).
# Формат: postgresql://пользователь:пароль@хост:порт/название_базы
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:123@localhost:5432/library"
)

# create_engine — создаёт "движок" подключения к базе.
# Само подключение ещё не открывается, просто настраивается.
# echo=True — в консоль будут выводиться все SQL запросы которые
# генерирует SQLAlchemy. Удобно при разработке, на продакшене убирают.
engine = create_engine(DATABASE_URL, echo=True)

# sessionmaker создаёт фабрику сессий.
# Сессия — это как "разговор" с базой данных:
# открыл, сделал запросы, закрыл.
# autocommit=False — изменения не сохраняются автоматически,
# нужно явно вызывать session.commit().
# autoflush=False — SQLAlchemy не отправляет незакоммиченные
# изменения в базу автоматически перед каждым запросом.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def create_tables():
    """Создаёт все таблицы в базе данных если их ещё нет.
    Вызывается один раз при запуске приложения.
    Если таблицы уже существуют — ничего не делает.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """Генератор сессии для FastAPI (Dependency Injection).

    FastAPI вызывает эту функцию автоматически когда роутеру нужна база.
    Сессия открывается, передаётся в роутер, и гарантированно закрывается
    после завершения запроса — даже если произошла ошибка (блок finally).

    Использование в роутере:
        from fastapi import Depends
        from database import get_db

        @router.get("/books")
        def get_books(db: Session = Depends(get_db)):
            return db.query(Book).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
