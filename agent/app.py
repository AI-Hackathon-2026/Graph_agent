import aiohttp
from dto import (
    GetGraphRequest,
    GetGraphResponse,
    GetTopicRequest,
    GetTopicResponse,
    NewCourseRequest,
    NewCourseResponse,
)
from pydantic import ValidationError

from agent.config import settings


async def get_graph(data: dict) -> dict:
    try:
        request_data = GetGraphRequest(**data)
    except ValidationError:
        return {
            "request_id": data.get("request_id"),
            "message": "Incorrect body in request",
        }

    try:
        async with aiohttp.ClientSession as session:
            async with session.get(
                settings.orchestrator_server, json=request_data.model_dump()
            ) as response:
                response.raise_for_status()
                response_date = GetGraphResponse(**await response.json())
                return response_date.model_dump()
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
        return {"request_id": data.get("request_id"), "message": f"Network error: {e}"}


async def get_topic(data: dict) -> dict:
    try:
        request_data = GetTopicRequest(**data)
    except ValidationError:
        return {
            "request_id": data.get("request_id"),
            "message": "Incorrect body in request",
        }

    try:
        async with aiohttp.ClientSession as session:
            async with session.get(
                settings.orchestrator_server, json=request_data.model_dump()
            ) as response:
                response.raise_for_status()
                response_date = GetTopicResponse(**await response.json())
                return response_date.model_dump()
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
        return {"request_id": data.get("request_id"), "message": f"Network error: {e}"}


async def new_course(data: dict) -> dict:
    try:
        request_data = NewCourseRequest(**data)
    except ValidationError:
        return {
            "request_id": data.get("request_id"),
            "message": "Incorrect body in request",
        }

    try:
        async with aiohttp.ClientSession as session:
            async with session.get(
                settings.orchestrator_server, json=request_data.model_dump()
            ) as response:
                response.raise_for_status()
                response_date = NewCourseResponse(**await response.json())
                return response_date.model_dump()
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
        return {"request_id": data.get("request_id"), "message": f"Network error: {e}"}


async def change_graph(data: dict) -> dict:
    pass
