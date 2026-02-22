import enum

from pydantic import BaseModel

from agent.graph import Graph, Topic


class ResponseCodes(enum.Enum):
    OK = 52
    INTERNAL_ERROR = 69
    BAD_REQUEST = 67


class GraphItem(BaseModel):
    graph_id: str


class TopicItem(BaseModel):
    topic_id: str


class GetGraphsRequest(BaseModel):
    request_id: str
    message: list[GraphItem]


class GetGraphsResponse(BaseModel):
    request_id: str
    message: list[Graph] | None
    status: ResponseCodes


class GetTopicRequest(BaseModel):
    request_id: str
    message: TopicItem


class GetTopicResponse(BaseModel):
    request_id: str
    message: Topic | None
    status: ResponseCodes


class DBLinks(BaseModel):
    link_id: str


class CreateCourseData(BaseModel):
    username: str
    requirements: str
    links: list[DBLinks]


class CreateCourseRequest(BaseModel):
    request_id: str
    message: CreateCourseData


class UsersGraph(BaseModel):
    username: str
    graph_id: str | None


class CreateCourseResponse(BaseModel):
    request_id: str
    message: UsersGraph | None
    status: ResponseCodes
