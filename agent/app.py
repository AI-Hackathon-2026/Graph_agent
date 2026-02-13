from typing import Any, Callable, Type, cast

import aiohttp
from langfuse import Langfuse, observe
from pydantic import ValidationError

from agent.config import application_hosts_setting, langfuse_settings
from agent.dto import (
    CreateCourseRequest,
    CreateCourseResponse,
    GetGraphsRequest,
    GetGraphsResponse,
    GetTopicRequest,
    GetTopicResponse,
)
from agent.dto import ResponseCodes

langfuse = Langfuse(
    secret_key=langfuse_settings.SECRET_KEY,
    public_key=langfuse_settings.PUBLIC_KEY,
    host=langfuse_settings.LANGFUSE_SERVER,
)


class OrchestratorClient:
    session: aiohttp.ClientSession

    async def start_http_session(self):
        self.session = aiohttp.ClientSession()

    @observe(name="request")
    async def request(
        self,
        request_class: Type[CreateCourseRequest | GetGraphsRequest | GetTopicRequest],
        response_class: Type[
            CreateCourseResponse | GetGraphsResponse | GetTopicResponse
        ],
        url: str,
        body: dict,
        http_method: str,
    ) -> CreateCourseResponse | GetGraphsResponse | GetTopicResponse:
        try:
            request_class(**body)
        except ValidationError:
            return response_class(
                **{
                    "request_id": body["request_id"],
                    "message": None,
                    "status": ResponseCodes.BAD_REQUEST
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
            message = (None,)
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
