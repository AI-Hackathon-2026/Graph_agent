from uuid import uuid4

from locust import HttpUser, task

from agent.dto import (
    CreateCourseData,
    CreateCourseRequest,
    DBLinks,
    GetGraphsPreviewRequest,
    GetGraphsRequest,
    GetTopicRequest,
    GraphItem,
    NodeItem,
    SetNodeAsEndedRequest,
    TopicItem,
)


class MyUser(HttpUser):
    @task(4)
    def get_graph(self):
        payload = GetGraphsRequest(
            request_id=str(uuid4()),
            message=[GraphItem(graph_id="69f856935180c24f271d42c0")],
        ).model_dump()
        self.client.get("/get_graph", json=payload)

    @task(4)
    def get_topic(self):
        payload = GetTopicRequest(
            request_id=str(uuid4()),
            message=TopicItem(topic_id="69f856835180c24f271d42b9"),
        ).model_dump()
        self.client.get("/get_topic", json=payload)

    @task(1)
    def create_course(self):
        payload = CreateCourseRequest(
            request_id=str(uuid4()),
            message=CreateCourseData(
                username="as", requirements="22", links=[DBLinks(link_id="123")]
            ),
        ).model_dump()
        self.client.post("/create_course", json=payload)

    @task(4)
    def get_graph_previews(self):
        payload = GetGraphsPreviewRequest(
            request_id=str(uuid4()),
            message=[GraphItem(graph_id="69f856935180c24f271d42c0")],
        ).model_dump()
        self.client.get("/get_graph_previews", json=payload)

    @task(2)
    def set_node_as_ended(self):
        payload = SetNodeAsEndedRequest(
            request_id=str(uuid4()),
            message=NodeItem(node_id="69f856935180c24f271d42c1"),
        ).model_dump()
        self.client.patch("/set_node_as_ended", json=payload)
