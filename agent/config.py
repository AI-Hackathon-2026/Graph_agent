from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    consumer_kafka_topic: str = "to_ml"
    producer_kafka_topic: str = "from_ml"

    bootstrap_servers: str = "localhost:9092"
    orchestrator_server: str = "http://localhost:8067"

    get_graph_link: str = "/get_graph"
    get_topic_link: str = "/get_topic"
    new_course_link: str = "/new_course"

    get_graph_key: str = "get_graph"
    get_topic_key: str = "get_topic"
    new_course_key: str = "new_course"
    change_graph_key: str = "change_graph"


settings = Settings()
