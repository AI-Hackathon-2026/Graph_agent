from pydantic import BaseModel


class Topic(BaseModel):
    topic_id: int
    title: str
    topic_content: str


class GraphNode(BaseModel):
    node_id: int
    topic_id: int
    studied: bool


class Graph(BaseModel):
    graph_id: str
    nodes: list[GraphNode]
