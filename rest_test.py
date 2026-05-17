import asyncio
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, Request, Response

from agent.config import kafka_settings
from agent.dto import (
    CreateCourseRequest,
    GetGraphsPreviewRequest,
    GetGraphsRequest,
    GetTopicRequest,
    SetNodeAsEndedRequest,
)
from lifespan import Kafka, lifespan

app = FastAPI(lifespan=lifespan)


def get_kafka(req: Request):
    return req.app.state.kafka


KAFKA_DEP = Annotated[Kafka, Depends(get_kafka)]


def create_event():
    event = asyncio.Event()
    return event


@app.get("/get_graph")
async def get_graph(req: GetGraphsRequest, kafka: KAFKA_DEP):
    event = create_event()
    kafka.requests[req.request_id] = event
    await kafka.producer.send(
        topic=kafka_settings.CONSUMER_KAFKA_TOPIC,
        key=kafka_settings.GET_GRAPH_KEY,
        value=(req.model_dump_json()).encode("utf-8"),
    )
    await event.wait()
    return Response(status_code=200)


@app.get("/get_topic")
async def get_topic(req: GetTopicRequest, kafka: KAFKA_DEP):
    event = create_event()

    kafka.requests[req.request_id] = event
    await kafka.producer.send(
        topic=kafka_settings.CONSUMER_KAFKA_TOPIC,
        key=kafka_settings.GET_TOPIC_KEY,
        value=(req.model_dump_json()).encode("utf-8"),
    )

    await event.wait()
    kafka.requests.pop(req.request_id)
    return Response(status_code=200)


@app.post("/create_course")
async def create_course(req: CreateCourseRequest, kafka: KAFKA_DEP):
    event = create_event()

    kafka.requests[req.request_id] = event
    await kafka.producer.send(
        topic=kafka_settings.CONSUMER_KAFKA_TOPIC,
        key=kafka_settings.CREATE_COURSE_KEY,
        value=(req.model_dump_json()).encode("utf-8"),
    )
    await event.wait()
    kafka.requests.pop(req.request_id)
    return Response(status_code=200)


@app.get("/get_graph_previews")
async def get_graph_previews(req: GetGraphsPreviewRequest, kafka: KAFKA_DEP):
    event = create_event()

    kafka.requests[req.request_id] = event
    await kafka.producer.send(
        topic=kafka_settings.CONSUMER_KAFKA_TOPIC,
        key=kafka_settings.GET_GRAPH_PREVIEWS_KEY,
        value=(req.model_dump_json()).encode("utf-8"),
    )
    await event.wait()
    kafka.requests.pop(req.request_id)
    return Response(status_code=200)


@app.patch("/set_node_as_ended")
async def set_node_as_ended(req: SetNodeAsEndedRequest, kafka: KAFKA_DEP):
    event = create_event()

    kafka.requests[req.request_id] = event
    await kafka.producer.send(
        topic=kafka_settings.CONSUMER_KAFKA_TOPIC,
        key=kafka_settings.SET_NODE_AS_ENDED,
        value=(req.model_dump_json()).encode("utf-8"),
    )
    await event.wait()
    kafka.requests.pop(req.request_id)
    return Response(status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=1488, backlog=4096)
