from pydantic import BaseModel

from agent.graph import Graph, Topic


class GraphItem(BaseModel):
    graph_id: int


class TopicItem(BaseModel):
    graph_id: int
    topic_id: int


class GetGraphsRequest(BaseModel):
    request_id: int
    message: list[GraphItem]


class GetGraphsResponse(BaseModel):
    request_id: int
    message: list[Graph]


class GetTopicRequest(BaseModel):
    request_id: int
    message: TopicItem


class GetTopicResponse(BaseModel):
    request_id: int
    message: Topic


class BdLinksItem(BaseModel):
    link_id: int


class CreateCourseItem(BaseModel):
    username: str
    requirements: str
    links: list[BdLinksItem]


class CreateCourseRequest(BaseModel):
    request_id: int
    message: CreateCourseItem


class CreateCourseResponse(BaseModel):
    request_id: int
    message: int
