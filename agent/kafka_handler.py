import base64
import json
from typing import Any

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from kafka.errors import KafkaError
from langfuse import Langfuse, observe
from loguru import logger

from agent.app import orchestrator_client
from agent.config import application_hosts_setting, kafka_settings, langfuse_settings
from agent.dto import (
    CreateCourseRequest,
    CreateCourseResponse,
    GetGraphsPreviewRequest,
    GetGraphsPreviewResponse,
    GetGraphsRequest,
    GetGraphsResponse,
    GetTopicRequest,
    GetTopicResponse,
)

langfuse = Langfuse(
    secret_key=langfuse_settings.SECRET_KEY,
    public_key=langfuse_settings.PUBLIC_KEY,
    host=langfuse_settings.LANGFUSE_SERVER,
)


class KafkaHandler:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            kafka_settings.CONSUMER_KAFKA_TOPIC,
            bootstrap_servers=application_hosts_setting.BOOTSTRAP_SERVER,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8"),
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=application_hosts_setting.BOOTSTRAP_SERVER,
            key_serializer=lambda k: str(k).encode("utf-8"),
        )
        logger.info(
            f"Ready to work, consume {kafka_settings.CONSUMER_KAFKA_TOPIC} topic"
        )

    async def consume(self):
        await self.consumer.start()
        await self.producer.start()
        await orchestrator_client.start_http_session()

        async for msg in self.consumer:
            logger.info(f"Message received. key: {msg.key}, value: {msg.value}")
            match msg.key:
                case kafka_settings.GET_GRAPH_KEY:
                    request_class = GetGraphsRequest
                    response_class = GetGraphsResponse
                    end_point = "/get_graphs"
                    http_method = "get"
                case kafka_settings.GET_TOPIC_KEY:
                    request_class = GetTopicRequest
                    response_class = GetTopicResponse
                    end_point = "/get_topic"
                    http_method = "get"
                case kafka_settings.CREATE_COURSE_KEY:
                    request_class = CreateCourseRequest
                    response_class = CreateCourseResponse
                    end_point = "/create_new_course"
                    http_method = "post"
                case kafka_settings.GET_GRAPH_PREVIEWS_KEY:
                    request_class = GetGraphsPreviewRequest
                    response_class = GetGraphsPreviewResponse
                    end_point = "/get_graph_previews"
                    http_method = "get"
                case _:
                    request_class = None
                    response_class = None
                    end_point = ""
                    http_method = ""
            if response_class is not None and response_class is not None:
                value = await orchestrator_client.request(
                    request_class=request_class,
                    response_class=response_class,
                    body={
                        "request_id": msg.value["request_id"],
                        "message": json.loads(
                            base64.b64decode(msg.value["message"]).decode("utf-8")
                        ),
                    },
                    url=end_point,
                    http_method=http_method,
                )
                await self.send_message(
                    kafka_settings.PRODUCER_KAFKA_TOPIC,
                    msg.key,
                    value.model_dump_json(),
                )

        await self.consumer.stop()
        await self.producer.stop()

    @observe(name="send_message")
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
            await self.producer.flush()
            return "The message has been sent"
        except KafkaError as e:
            return f"Kafka error: {e}"
