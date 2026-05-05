import random
import uuid
from time import sleep

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_rabbitmq
from api.rabbitmq import RabbitMQ
from api.schemas import ResultSchema, ScheduleResponse, TaskState
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
async def process_schedule(
    rabbitmq: RabbitMQ = Depends(get_rabbitmq),  # noqa: B008
) -> ScheduleResponse:
    task_id = str(uuid.uuid4())

    tasks.create(task_id)

    await rabbitmq.publish_json({"task_id": task_id})

    return ScheduleResponse(status="accepted", task_id=task_id)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskState,
)
def get_task_status(task_id: str) -> TaskState:
    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskState(**task)
