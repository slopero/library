from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from data.database import create_tables
from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.books import router as books_router
from routers.cart_favorites import cart_router, favorites_router, purchases_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Онлайн-библиотека Идея",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(cart_router)
app.include_router(favorites_router)
app.include_router(purchases_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)