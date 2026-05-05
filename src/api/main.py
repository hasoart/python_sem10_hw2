from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="Homework 2",
    version="0.6.7",
)

app.include_router(router)
