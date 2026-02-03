from pydantic import BaseModel

from agent.graph import Graph, Topic


class GraphItem(BaseModel):
    graph_id: int


class TopicItem(BaseModel):
    graph_id: int
    topic_id: int


class GetGraphRequest(BaseModel):
    request_id: int
    message: list[GraphItem]


class GetGraphResponse(BaseModel):
    request_id: int
    message: list[Graph] | str


class GetTopicRequest(BaseModel):
    request_id: int
    message: TopicItem


class GetTopicResponse(BaseModel):
    request_id: int
    message: Topic | str


class BdLinksItem(BaseModel):
    link_id: int


class NewCourseItem(BaseModel):
    username: str
    requirements: str
    links: list[BdLinksItem]


class NewCourseRequest(BaseModel):
    request_id: int
    message: NewCourseItem


class NewCourseResponse(BaseModel):
    request_id: int
    message: int | str


class ChangeGraphRequest(BaseModel):
    pass


class ChangeGraphResponse(BaseModel):
    pass
