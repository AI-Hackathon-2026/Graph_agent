import asyncio
import json
from contextlib import asynccontextmanager

import uvicorn
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI

from agent.config import application_hosts_setting, kafka_settings


async def goon():
    uvicorn.run("rest_test:app", host="127.0.0.1", port=1488)


class Kafka:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            kafka_settings.PRODUCER_KAFKA_TOPIC,
            bootstrap_servers=application_hosts_setting.BOOTSTRAP_SERVER,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8"),
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=application_hosts_setting.BOOTSTRAP_SERVER,
            key_serializer=lambda k: str(k).encode("utf-8"),
        )
        self.requests: dict[str, asyncio.Event] = {}

    async def start(self):
        await self.producer.start()
        await self.consumer.start()

    async def stop(self):
        await self.producer.flush()
        await self.producer.stop()
        await self.consumer.stop()

    async def consume(self):
        async for msg in self.consumer:
            self.requests[msg.value["request_id"]].set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    kafka = Kafka()
    await kafka.start()
    app.state.kafka = kafka
    asyncio.ensure_future(kafka.consume())
    yield
    await kafka.stop()
