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
    ) -> dict:
        try:
            request_class(**body)
        except ValidationError:
            return {
                "request_id": body["request_id"],
                "message": "Incorrect body in request",
            }

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
                response_data = response_class(**await response.json())
                return response_data.model_dump()

        except ValidationError:
            return {
                "request_id": body["request_id"],
                "message": None,
                "status": "Incorrect data from orchestrator",
            }

        except TimeoutError:
            return {
                "request_id": body["request_id"],
                "message": None,
                "status": "Timeout while calling orchestrator",
            }

        except aiohttp.ClientResponseError as e:
            return {
                "request_id": body["request_id"],
                "message": None,
                "status": f"HTTP error: {e.status}",
            }

        except aiohttp.ClientError as e:
            return {
                "request_id": body["request_id"],
                "message": None,
                "status": f"Network error: {e}",
            }


orchestrator_client = OrchestratorClient()
