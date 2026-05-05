import random
import uuid
from time import sleep

from fastapi import APIRouter, status

from api.schemas import ResultSchema, ScheduleResponse
from db import tasks

router = APIRouter(prefix="/process", tags=["Process"])


@router.post(
    "/sync",
    status_code=status.HTTP_200_OK,
    response_model=ResultSchema,
    name="Blocking heavy task",
    description="Generate random integer [1, 100000] using heavy algorithm (blocks for ~1 second).",
)
def process_sync() -> ResultSchema:
    sleep_time_sec = 1 + 0.02 * random.random()
    sleep(sleep_time_sec)

    return ResultSchema(result=random.randint(1, 100_000))


@router.post(
    "/schedule",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ScheduleResponse,
    name="Schedule heavy task",
    description="Schedule generating random integer [1, 100000] using heavy algorithm.",
)
def process_schedule() -> ScheduleResponse:
    task_id = str(uuid.uuid4())

    tasks.create(task_id)

    return ScheduleResponse(status="accepted", task_id=task_id)
