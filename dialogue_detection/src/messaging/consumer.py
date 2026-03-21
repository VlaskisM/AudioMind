import json
from collections.abc import Callable, Awaitable

import aio_pika

from src.configs.rabbitmq import rabbitmq_settings


class RabbitMQConsumer:

    def __init__(self, on_message: Callable[[dict], Awaitable[None]]):
        self._on_message = on_message
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None

    async def start(self):
        self._connection = await aio_pika.connect_robust(rabbitmq_settings.url)
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(rabbitmq_settings.DIARIZATION_QUEUE, durable=True)
        await queue.consume(self._handle)

    async def _handle(self, message: aio_pika.abc.AbstractIncomingMessage):
        async with message.process():
            body = json.loads(message.body.decode())
            await self._on_message(body)

    async def close(self):
        if self._connection:
            await self._connection.close()
