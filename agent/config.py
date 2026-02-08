import os

from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):
    CONSUMER_KAFKA_TOPIC: str = "to_ml"
    PRODUCER_KAFKA_TOPIC: str = "from_ml"

    GET_GRAPH_KEY: str = "get_graph"
    GET_TOPIC_KEY: str = "get_topic"
    CREATE_COURSE_KEY: str = "create_course"


class ApplicationHostsSettings(BaseSettings):
    BOOTSTRAP_SERVER: str = "kafka:9092"
    ORCHESTRATOR_SERVER: str = "http://orchestrator:8067"


class LangfuseSettings(BaseSettings):
    SECRET_KEY: str = os.environ.get("LANGFUSE_SECRET_KEY")
    PUBLIC_KEY: str = os.environ.get("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SERVER: str = "https://cloud.langfuse.com"


langfuse_settings = LangfuseSettings()
application_hosts_setting = ApplicationHostsSettings()
kafka_settings = KafkaSettings()
