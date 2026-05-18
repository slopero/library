from fastapi import FastAPI

from routers.health import router as health_router

app = FastAPI(title="Онлайн-библиотека Идея")

app.include_router(health_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)