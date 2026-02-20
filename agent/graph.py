from __future__ import annotations

from pydantic import BaseModel


class Topic(BaseModel):
    topic_id: str
    title: str
    topic_content: str


class GraphNode(BaseModel):
    node_id: str
    topic_id: str
    is_studied: bool
    is_major: bool
    prev_node_id: str | None
    next_node_id: str | None


class UsersGraphNode(BaseModel):
    node_id: str
    topic_id: str
    title: str
    is_studied: bool
    is_major: bool
    next_node_id: str | None


class Graph(BaseModel):
    graph_id: str
    nodes: list[UsersGraphNode]
