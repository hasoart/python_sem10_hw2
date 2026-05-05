from typing import Literal

from pydantic import BaseModel

TaskStatus = Literal["queued", "processing", "finished", "failed"]


class ResultSchema(BaseModel):
    result: int


class ScheduleResponse(BaseModel):
    status: Literal["accepted"]
    task_id: str


class TaskState(BaseModel):
    task_id: str
    status: TaskStatus
    result: int | None = None
    error: str | None = None
