from fastapi import FastAPI
from routers import books


app = FastAPI(title="Онлайн-библиотека Идея")
app.include_router(books.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)