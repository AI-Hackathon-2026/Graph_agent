import asyncio
import json

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from langfuse import Langfuse, observe

from agent.app import orchestrator_client
from agent.config import application_hosts_setting, kafka_settings, langfuse_settings
from agent.dto import (
    CreateCourseRequest,
    CreateCourseResponse,
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
        self.consumer = KafkaConsumer(
            kafka_settings.CONSUMER_KAFKA_TOPIC,
            bootstrap_servers=application_hosts_setting.BOOTSTRAP_SERVER,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8"),
        )
        self.producer = KafkaProducer(
            bootstrap_servers=application_hosts_setting.BOOTSTRAP_SERVER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: str(k).encode("utf-8"),
        )

    async def main(self):
        await orchestrator_client.start_http_session()
        for msg in self.consumer:
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
                case _:
                    request_class = None
                    response_class = None
                    end_point = ""
                    http_method = ""
            if response_class is None and response_class is None:
                value = {
                    "request_id": msg.value["request_id"],
                    "message": "Incorrect key in message",
                }
            else:
                value = await orchestrator_client.request(
                    request_class=request_class,
                    response_class=response_class,
                    body=msg.value,
                    url=end_point,
                    http_method=http_method,
                )
            await self.send_message(
                kafka_settings.PRODUCER_KAFKA_TOPIC, msg.key, value.model_dump_json()
            )

    @observe(name="send_message")
    async def send_message(self, topic: str, key: str, value: dict) -> None | str:
        try:
            self.producer.send(
                topic=topic,
                key=key,
                value=value,
            )
            return "The message has been sent"
        except KafkaError as e:
            return f"Kafka error: {e}"


if __name__ == "__main__":
    kafka_handler = KafkaHandler()
    asyncio.run(kafka_handler.main())
