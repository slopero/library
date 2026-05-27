from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from data.database import create_tables
from fastapi import FastAPI
from routers.auth import admin_router, user_router
from routers.books import router as books_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Онлайн-библиотека Идея", 
    lifespan=lifespan,
    redirect_slashes=False,  # отключаем автоматическое добавление слэша в конце URL              
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books_router)
app.include_router(user_router)
app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)