import datetime
import time
from functools import wraps
from queue import Queue
from time import sleep

import psutil
from typing import Type
from collections import deque
from agent.config import postgres_settings
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from agent.dto import (
    CreateCourseRequest,
    GetGraphsPreviewRequest,
    GetGraphsRequest,
    GetTopicRequest,
)
from agent.sql_models import (
    CreateCourseMetric,
    GetGraphsMetric,
    GetGraphsPreviewMetric,
    GetTopicMetric,
    Metric,
)


class MetricsCollector:
    def __init__(self, engine: AsyncEngine):
        self.metrics_queue = Queue(maxsize=1000)
        self.engine = engine
        self.cpu_load = deque()
        self.mem_load = 0.0
        self.async_session_maker = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

    def add_metric_to_queue(self, metric: Metric):
        self.metrics_queue.put(metric)

    @property
    def cpu_load_avg(self) -> float:
        return sum(self.cpu_load) / len(self.cpu_load)

    def load_check(self):
        while True:
            self.cpu_load.append(psutil.cpu_percent(interval=None))
            if len(self.cpu_load) > 5:
                self.cpu_load.pop()
            self.mem_load = psutil.virtual_memory().percent
            sleep(0.1)

    async def write_metrics(self):
        self.load_check()
        async with self.async_session_maker() as session:
            while True:
                while self.cpu_load_avg < 70 and self.mem_load < 75 and not self.metrics_queue.empty():
                    session.add(self.metrics_queue.get())
                await session.commit()

metrics_collector = MetricsCollector(create_async_engine(postgres_settings.URL))


def metrics(foo):
    @wraps(foo)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await foo(*args, **kwargs)
        end = time.time()

        exec_time = end - start
        date_time = datetime.datetime.now(datetime.UTC)

        request_class: Type = args[0]
        body: dict = args[3]
        request = request_class(**body)

        match request_class:
            case GetTopicRequest():
                metric = GetTopicMetric(topic_id=request.message.topic_id)
            case GetGraphsRequest():
                graph_ids = [graph.graph_id for graph in request.message]
                metric = GetGraphsMetric(graph_ids=graph_ids)
            case GetGraphsPreviewRequest():
                graph_ids = [graph.graph_id for graph in request.message]
                metric = GetGraphsPreviewMetric(graph_ids=graph_ids)
            case CreateCourseRequest():
                metric = CreateCourseMetric(
                    username=request.message.username, graph_id=result.message.graph_id
                )
            case _:
                return result
        metric.exec_time, metric.date_time, metric.status = (
            exec_time,
            date_time,
            result.status.name,
        )

        metrics_collector.add_metric_to_queue(metric)

        return result

    return wrapper
