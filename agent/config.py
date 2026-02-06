from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CONSUMER_KAFKA_TOPIC: str = "to_ml"
    PRODUCER_KAFKA_TOPIC: str = "from_ml"

    BOOTSTRAP_SERVER: str = "127.0.0.1:9092"
    ORCHESTRATOR_SERVER: str = "http://127.0.0.1:8067"

    GET_GRAPH_KEY: str = "get_graph"
    GET_TOPIC_KEY: str = "get_topic"
    CREATE_COURSE_KEY: str = "create_course"

    LANGFUSE_SERVER: str = "https://cloud.langfuse.com"


settings = Settings()
