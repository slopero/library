from fastapi import FastAPI
from routers import books
from data.database import create_tables
from contextlib import asynccontextmanager
import models.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()  # Создаём таблицы при старте приложения
    yield  # Здесь будет выполняться обработка запросов

app = FastAPI(title="Онлайн-библиотека Идея", lifespan=lifespan)
app.include_router(books.router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)