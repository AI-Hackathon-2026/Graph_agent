import asyncio
import json
from asyncio import CancelledError

from aiokafka import AIOKafkaConsumer
from loguru import logger

from agent.app import OrchestratorClient
from agent.config import application_hosts_setting, kafka_settings
from agent.dto import (
    CreateCourseRequest,
    CreateCourseResponse,
    GetGraphsPreviewRequest,
    GetGraphsPreviewResponse,
    GetGraphsRequest,
    GetGraphsResponse,
    GetTopicRequest,
    GetTopicResponse,
    SetNodeAsEndedRequest,
    SetNodeAsEndedResponse,
)


class KafkaHandler:
    def __init__(self, orc_client: OrchestratorClient):
        self.orc_client = orc_client
        self.consumer = AIOKafkaConsumer(
            kafka_settings.CONSUMER_KAFKA_TOPIC,
            bootstrap_servers=application_hosts_setting.BOOTSTRAP_SERVER,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8"),
        )

    async def start(self):
        await self.consumer.start()
        logger.info(
            f"Kafka is started, consume {kafka_settings.CONSUMER_KAFKA_TOPIC} topic"
        )

    async def stop(self):
        await self.consumer.stop()

    async def consume(self):
        try:
            await self.start()
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
                    case kafka_settings.SET_NODE_AS_ENDED:
                        request_class = SetNodeAsEndedRequest
                        response_class = SetNodeAsEndedResponse
                        end_point = "/set_node_as_ended"
                        http_method = "patch"
                    case _:
                        request_class = None
                        response_class = None
                        end_point = ""
                        http_method = ""
                if response_class is not None and response_class is not None:
                    asyncio.create_task(
                        self.orc_client.request(
                            request_class=request_class,
                            response_class=response_class,
                            body={
                                "request_id": msg.value["request_id"],
                                "message": msg.value["message"],
                            },
                            url=end_point,
                            http_method=http_method,
                            key=msg.key,
                        )
                    )
        except CancelledError:
            await self.stop()
            logger.info("Kafka is canceled")
