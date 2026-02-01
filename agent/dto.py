from pydantic import BaseModel


class GraphItem(BaseModel):
    graph_id: int


class TopicItem(BaseModel):
    graph_id: int
    topic_id: int


class GetGraphRequest(BaseModel):
    request_id: int
    message: list[GraphItem]


class GetGraphResponse(BaseModel):
    zaglushka: int


class GetTopicRequest(BaseModel):
    request_id: int
    message: TopicItem


class GetTopicResponse(BaseModel):
    zaglushka: int


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
    zaglushka: int


class ChangeGraphRequest(BaseModel):
    pass


class ChangeGraphResponse(BaseModel):
    pass
