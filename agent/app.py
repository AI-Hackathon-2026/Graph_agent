from typing import Any, Callable, Type, cast

import aiohttp
from aiohttp import TCPConnector
from pydantic import ValidationError

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
    ResponseCodes,
)
from agent.kafka_producer import KafkaProducer


class OrchestratorClient:
    session: aiohttp.ClientSession

    def __init__(self, producer: KafkaProducer):
        self.producer = producer

    async def start_http_session(self):
        connector = TCPConnector(
            limit=2000,
        )
        self.session = aiohttp.ClientSession(connector=connector)

    async def close_http_session(self):
        await self.session.close()

    # @metrics_collector.metrics
    async def request(
        self,
        request_class: Type[
            CreateCourseRequest
            | GetGraphsRequest
            | GetTopicRequest
            | GetGraphsPreviewRequest
        ],
        response_class: Type[
            CreateCourseResponse
            | GetGraphsResponse
            | GetTopicResponse
            | GetGraphsPreviewResponse
        ],
        url: str,
        body: dict,
        http_method: str,
        key: str,
    ):
        try:
            request_class(**body)
        except ValidationError:
            return response_class(
                **{
                    "request_id": body["request_id"],
                    "message": None,
                    "status": ResponseCodes.BAD_REQUEST,
                }
            )

        method_mapping = {
            "get": self.session.get,
            "post": self.session.post,
            "patch": self.session.patch,
        }
        try:
            was_exception = False
            session_method = cast(
                Callable[..., Any], method_mapping.get(http_method.lower())
            )
            if session_method is None:
                raise ValueError(f"Unsupported HTTP method: {http_method}")
            async with session_method(
                application_hosts_setting.ORCHESTRATOR_SERVER + url, json=body
            ) as response:
                response.raise_for_status()
                response = response_class(**await response.json())

        except ValidationError:
            message = None
            status = ResponseCodes.INTERNAL_ERROR
            was_exception = True

        except TimeoutError:
            message = None
            status = ResponseCodes.INTERNAL_ERROR
            was_exception = True

        except aiohttp.ClientResponseError:
            message = None
            status = ResponseCodes.INTERNAL_ERROR
            was_exception = True

        except aiohttp.ClientError:
            message = None
            status = ResponseCodes.INTERNAL_ERROR
            was_exception = True
        if was_exception:
            response = response_class(
                **{
                    "request_id": body["request_id"],
                    "message": message,
                    "status": status,
                }
            )
        await self.producer.send_message(
            topic=kafka_settings.PRODUCER_KAFKA_TOPIC,
            key=key,
            value=response.model_dump_json(),
        )
