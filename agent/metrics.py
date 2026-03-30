import asyncio
import datetime
import time
from asyncio import Queue
from collections import deque
from functools import wraps
from typing import Type

import psutil
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

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


class LoadMonitor:
    def __init__(self):
        self.cpu_load = deque()
        self.mem_load = 0.0

    @property
    def cpu_load_avg(self) -> float:
        return 0 if not len(self.cpu_load) else sum(self.cpu_load) / len(self.cpu_load)

    async def load_check(self):
        logger.info("Load check started")
        while True:
            self.cpu_load.append(psutil.cpu_percent(interval=None))
            if len(self.cpu_load) > 5:
                self.cpu_load.pop()
            self.mem_load = psutil.virtual_memory().percent
            await asyncio.sleep(0.1)


class MetricsCollector:
    def __init__(self, engine: AsyncEngine, load_monitor: LoadMonitor):
        self.metrics_queue = Queue(maxsize=1000)
        self.engine = engine
        self.load_monitor = load_monitor
        self.async_session_maker = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

    async def add_metric_to_queue(self, metric: Metric):
        await self.metrics_queue.put(metric)

    async def write_metrics(self):
        logger.info("Metrics writer started")
        async with self.async_session_maker() as session:
            while True:
                metric = await self.metrics_queue.get()
                if (
                    self.load_monitor.cpu_load_avg < 70
                    and self.load_monitor.mem_load < 75
                ):
                    session.add(metric)
                    await session.commit()
                    logger.info("Metric saved")

    def metrics(self, foo):
        @wraps(foo)
        async def wrapper(*args, **kwargs):
            print(kwargs)
            start = time.time()
            result = await foo(*args, **kwargs)
            end = time.time()

            exec_time = end - start
            date_time = datetime.datetime.now(datetime.UTC)
            request_class: Type = args[0]
            body: dict = args[3]
            request = request_class(**body)

            if isinstance(request, GetTopicRequest):
                metric = GetTopicMetric(topic_id=request.message.topic_id)
            elif isinstance(request, GetGraphsRequest):
                graph_ids = [graph.graph_id for graph in request.message]
                metric = GetGraphsMetric(graph_ids=graph_ids)
            elif isinstance(request, GetGraphsPreviewRequest):
                graph_ids = [graph.graph_id for graph in request.message]
                metric = GetGraphsPreviewMetric(graph_ids=graph_ids)
            elif isinstance(request, CreateCourseRequest):
                metric = CreateCourseMetric(
                    username=request.message.username, graph_id=result.message.graph_id
                )
            else:
                return result

            metric.exec_time, metric.date_time, metric.status = (
                exec_time,
                date_time,
                result.status.name,
            )

            await self.add_metric_to_queue(metric)

            return result

        return wrapper
