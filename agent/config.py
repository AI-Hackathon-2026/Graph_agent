import json

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    consumer_kafka_topic: str = "to_ml"
    producer_kafka_topic: str = "from_ml"

    bootstrap_servers: str = "localhost:9092"
    orchestrator_server: str = "localhost: 8067"

    @staticmethod
    def value_deserializer(v):
        return json.loads(v.decode("utf-8"))

    @staticmethod
    def value_serializer(v):
        return json.dumps(v).encode("utf-8")

    get_graph_key: str = b"get_graph"
    get_topic_key: str = b"get_topic"
    new_course_key: str = b"new_course"
    change_graph_key: str = b"change_graph"


settings = Settings()
