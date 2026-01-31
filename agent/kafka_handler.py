import asyncio

from kafka import KafkaConsumer, KafkaProducer

from agent.app import get_graph, get_topic, new_course
from agent.config import settings

consumer = KafkaConsumer(
    settings.consumer_kafka_topic,
    bootstrap_servers=settings.bootstrap_servers,
    value_deserializer=settings.value_deserializer,
)
producer = KafkaProducer(
    bootstrap_servers=settings.bootstrap_servers,
    value_serializer=settings.value_serializer,
)


async def main():
    for msg in consumer:
        if msg.key == settings.get_graph_key:
            producer.send(
                topic=settings.producer_kafka_topic,
                key=settings.get_graph_key,
                value=await get_graph(msg.value),
            )

        elif msg.key == settings.get_topic_key:
            producer.send(
                topic=settings.producer_kafka_topic,
                key=settings.get_topic_key,
                value=await get_topic(msg.value),
            )

        elif msg.key == settings.new_course_key:
            producer.send(
                topic=settings.producer_kafka_topic,
                key=settings.new_course_key,
                value=await new_course(msg.value),
            )

        elif msg.key == settings.change_graph_key:
            pass


if __name__ == "__main__":
    asyncio.run(main())
