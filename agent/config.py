from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    consumer_kafka_topic: str = "to_ml"
    producer_kafka_topic: str = "from_ml"

    bootstrap_servers: str = "127.0.0.1:9092"
    orchestrator_server: str = "http://127.0.0.1:8067"

    get_graph_key: str = "get_graph"
    get_topic_key: str = "get_topic"
    new_course_key: str = "create_course"


settings = Settings()
