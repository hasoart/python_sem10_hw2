import random
from time import sleep

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["Process"])


class ResultSchema(BaseModel):
    result: int


@router.post(
    "/process/sync",
    status_code=status.HTTP_200_OK,
    response_model=ResultSchema,
    name="Blocking heavy task",
    description="Generate random integer [1, 100000] using heavy algorithm (blocks for ~1 second)."
)
def process_sync() -> ResultSchema:
    sleep_time_sec = 1 + 0.02 * random.random()
    sleep(sleep_time_sec)

    return ResultSchema(result=random.randint(1, 100_000))
