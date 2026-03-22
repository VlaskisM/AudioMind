import json

import aio_pika

from src.configs.rabbitmq import rabbitmq_settings


class RabbitMQPublisher:

    def __init__(self):
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(rabbitmq_settings.url)
        self._channel = await self._connection.channel()
        await self._channel.declare_queue(rabbitmq_settings.NEXT_QUEUE, durable=True)

    async def publish(self, recording_id: int) -> None:
        if self._channel is None:
            await self.connect()

        message = aio_pika.Message(
            body=json.dumps({
                "recording_id": recording_id,
            }).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await self._channel.default_exchange.publish(
            message,
            routing_key=rabbitmq_settings.NEXT_QUEUE,
        )

    async def close(self):
        if self._connection:
            await self._connection.close()
