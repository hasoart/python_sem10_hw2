from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.dependencies import rabbitmq
from api.routes import router
from db.tasks import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001 ANN201
    init_db()
    await rabbitmq.connect()

    yield

    await rabbitmq.close()


app = FastAPI(
    title="Homework 2",
    version="0.6.7",
    lifespan=lifespan,
)

app.include_router(router)
