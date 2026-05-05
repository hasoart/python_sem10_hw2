import json
from typing import TYPE_CHECKING

import aio_pika

from core.config import settings

if TYPE_CHECKING:
    from aio_pika.abc import AbstractChannel, AbstractRobustConnection


class RabbitMQ:
    def __init__(self) -> None:
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue(settings.task_queue_name, durable=True)

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()

    async def publish_json(self, payload: dict) -> None:
        if self.channel is None:
            raise RuntimeError("RabbitMQ channel is not initialized")

        message = aio_pika.Message(
            body=json.dumps(payload).encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=settings.task_queue_name,
        )
