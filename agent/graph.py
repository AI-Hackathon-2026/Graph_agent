from pydantic import BaseModel


class Topic(BaseModel):
    topic_id: int
    title: str
    context: str


class GraphNode(BaseModel):
    node_id: int
    topic_id: int
    studied: bool


class Graph(BaseModel):
    graph_id: int
    nodes: list[GraphNode]
