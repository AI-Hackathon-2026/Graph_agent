from typing import Type

import aiohttp
from pydantic import BaseModel, ValidationError

from agent.config import settings
from agent.dto import CreateCourseRequest  # noqa: F401
from agent.dto import CreateCourseResponse  # noqa: F401
from agent.dto import GetGraphsRequest  # noqa: F401
from agent.dto import GetGraphsResponse  # noqa: F401
from agent.dto import GetTopicRequest  # noqa: F401
from agent.dto import GetTopicResponse  # noqa: F401


class OrchestratorClient:
    session: aiohttp.ClientSession

    async def start_http_session(self):
        self.session = aiohttp.ClientSession()

    async def request(
        self,
        request_class: Type[BaseModel],
        response_class: Type[BaseModel],
        end_point: str,
        data: dict,
        http_method: str,
    ) -> dict:
        try:
            request_data = request_class(**data)
        except ValidationError:
            return {
                "request_id": data.get("request_id"),
                "message": "Incorrect body in request",
            }
        try:
            if http_method == "get":
                async with self.session.get(
                    settings.orchestrator_server + end_point,
                    json=request_data.model_dump(),
                ) as response:
                    response.raise_for_status()
                    response_data = response_class(**await response.json())
                    return response_data.model_dump()
            else:
                async with self.session.post(
                    settings.orchestrator_server + end_point,
                    json=request_data.model_dump(),
                ) as response:
                    response.raise_for_status()
                    response_data = response_class(**await response.json())
                    return response_data.model_dump()
        except ValidationError:
            return {
                "request_id": data.get("request_id"),
                "message": "Incorrect data from orchestrator",
            }

        except TimeoutError:
            return {
                "request_id": data.get("request_id"),
                "message": "Timeout while calling orchestrator",
            }

        except aiohttp.ClientResponseError as e:
            return {
                "request_id": data.get("request_id"),
                "message": f"HTTP error: {e.status}",
            }

        except aiohttp.ClientError as e:
            return {
                "request_id": data.get("request_id"),
                "message": f"Network error: {e}",
            }


orchestrator_client = OrchestratorClient()
