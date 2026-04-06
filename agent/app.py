from typing import Any, Callable, Type, cast

import aiohttp
from pydantic import ValidationError

from agent.config import application_hosts_setting
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
from agent.main import metrics_collector


class OrchestratorClient:
    session: aiohttp.ClientSession

    async def start_http_session(self):
        self.session = aiohttp.ClientSession()

    async def close_http_session(self):
        await self.session.close()

    @metrics_collector.metrics
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
    ) -> CreateCourseResponse | GetGraphsResponse | GetTopicResponse | GetGraphsPreviewResponse:
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
        }
        try:
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
                return response

        except ValidationError:
            message = None
            status = ResponseCodes.INTERNAL_ERROR

        except TimeoutError:
            message = None
            status = ResponseCodes.INTERNAL_ERROR

        except aiohttp.ClientResponseError:
            message = None
            status = ResponseCodes.INTERNAL_ERROR

        except aiohttp.ClientError:
            message = None
            status = ResponseCodes.INTERNAL_ERROR
        return response_class(
            **{"request_id": body["request_id"], "message": message, "status": status}
        )


orchestrator_client = OrchestratorClient()
