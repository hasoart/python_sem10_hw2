import asyncio
import json
import os
import random
from time import sleep

import aio_pika

from core.config import settings
from db import tasks


def heavy_algorithm() -> int:
    sleep_time_sec = 1 + 0.02 * random.random()
    sleep(sleep_time_sec)
    return random.randint(1, 100_000)


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        payload = json.loads(message.body.decode("utf-8"))
        task_id = payload["task_id"]

        worker_pid = os.getpid()
        print(f"[worker {worker_pid}] processing task {task_id}")

        try:
            tasks.update(task_id, status="processing")

            result = heavy_algorithm()

            tasks.update(
                task_id=task_id,
                status="finished",
                result=result,
            )

            print(f"[worker {worker_pid}] finished task {task_id}")

        except Exception as exc:
            tasks.update(
                task_id=task_id,
                status="failed",
                error=str(exc),
            )
            raise


async def main() -> None:
    tasks.init_db()

    connection = await aio_pika.connect_robust(settings.rabbitmq_url)

    async with connection:
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(
            settings.task_queue_name,
            durable=True,
        )

        await queue.consume(handle_message)

        print(f"Worker started. PID={os.getpid()}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
