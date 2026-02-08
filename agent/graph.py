from __future__ import annotations

from pydantic import BaseModel


class Topic(BaseModel):
    topic_id: str
    title: str
    topic_content: str


class GraphNode(BaseModel):
    node_id: str
    topic_id: str
    studied: bool
    is_major: bool
    prev_node: GraphNode | None
    next_node: GraphNode | None


class Graph(BaseModel):
    graph_id: str
    first_node: GraphNode
