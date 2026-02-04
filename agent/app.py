from typing import Type

import aiohttp
from dto import CreateCourseRequest  # noqa: F401
from dto import CreateCourseResponse  # noqa: F401
from dto import GetGraphsRequest  # noqa: F401
from dto import GetGraphsResponse  # noqa: F401
from dto import GetTopicRequest  # noqa: F401
from dto import GetTopicResponse  # noqa: F401
from pydantic import BaseModel, ValidationError

from agent.config import settings


class OrchestratorClient:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def request(
        self,
        request_class: Type[BaseModel],
        response_class: Type[BaseModel],
        data: dict,
    ) -> dict:
        try:
            request_data = request_class(**data)
        except ValidationError:
            return {
                "request_id": data.get("request_id"),
                "message": "Incorrect body in request",
            }
        try:
            async with self.session.get(
                settings.orchestrator_server + settings.get_graph_link,
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
