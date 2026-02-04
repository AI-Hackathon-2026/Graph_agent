import asyncio
import json

from kafka import KafkaConsumer, KafkaProducer

from agent.app import orchestrator_client
from agent.config import settings
from agent.dto import (
    CreateCourseRequest,
    CreateCourseResponse,
    GetGraphsRequest,
    GetGraphsResponse,
    GetTopicRequest,
    GetTopicResponse,
)

consumer = KafkaConsumer(
    settings.consumer_kafka_topic,
    bootstrap_servers=settings.bootstrap_servers,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    key_deserializer=lambda k: k.decode("utf-8"),
)
producer = KafkaProducer(
    bootstrap_servers=settings.bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: str(k).encode("utf-8"),
)


async def main():
    for msg in consumer:
        match msg.key:
            case settings.get_graph_key:
                value = await orchestrator_client.request(
                    request_class=GetGraphsRequest,
                    response_class=GetGraphsResponse,
                    data=msg.value,
                )
            case settings.get_topic_link:
                value = await orchestrator_client.request(
                    request_class=GetTopicRequest,
                    response_class=GetTopicResponse,
                    data=msg.value,
                )
            case settings.new_course_key:
                value = await orchestrator_client.request(
                    request_class=CreateCourseRequest,
                    response_class=CreateCourseResponse,
                    data=msg.value,
                )
            case _:
                value = {
                    "request_id": msg.value["request_id"],
                    "message": "Incorrect key in message",
                }
        await send_message(settings.producer_kafka_topic, msg.key, value)


async def send_message(topic: str, key: str, value: dict):
    producer.send(
        topic=topic,
        key=key,
        value=value,
    )


if __name__ == "__main__":
    asyncio.run(main())
