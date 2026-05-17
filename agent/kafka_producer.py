from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from loguru import logger

from agent.config import application_hosts_setting


class KafkaProducer:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=application_hosts_setting.BOOTSTRAP_SERVER,
            key_serializer=lambda k: str(k).encode("utf-8"),
        )

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.flush()
        await self.producer.stop()

    async def send_message(self, topic: str, key: str, value: Any) -> None | str:
        try:
            await self.producer.send(
                topic=topic,
                key=key,
                value=value.encode("utf-8"),
            )
            logger.info(
                f"The message has been sent. topic: {topic}, key: {key}, value: {value}"
            )
            return "The message has been sent"
        except KafkaError as e:
            return f"Kafka error: {e}"
