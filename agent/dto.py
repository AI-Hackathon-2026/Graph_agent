from pydantic import BaseModel

from agent.graph import Graph, Topic


class GraphItem(BaseModel):
    graph_id: str


class TopicItem(BaseModel):
    graph_id: str
    topic_id: str


class GetGraphsRequest(BaseModel):
    request_id: str
    message: list[GraphItem]


class GetGraphsResponse(BaseModel):
    request_id: str
    message: list[Graph] | None
    status: int


class GetTopicRequest(BaseModel):
    request_id: str
    message: TopicItem


class GetTopicResponse(BaseModel):
    request_id: str
    message: Topic | None
    status: int


class BdLinksItem(BaseModel):
    link_id: str


class CreateCourseRequestItem(BaseModel):
    username: str
    requirements: str
    links: list[BdLinksItem]


class CreateCourseRequest(BaseModel):
    request_id: str
    message: CreateCourseRequestItem


class CreateCourseResponseItem(BaseModel):
    username: str
    graph_id: str | None


class CreateCourseResponse(BaseModel):
    request_id: str
    message: CreateCourseResponseItem | None
    status: int
