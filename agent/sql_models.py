from sqlalchemy import ARRAY, Column, DateTime, Float, String
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Metric(Base):
    __abstract__ = True

    date_time = Column(DateTime, nullable=False)
    exec_time = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(date_time={self.date_time}, exec_time={self.exec_time}, status='{self.status}')>"


class CreateCourseMetric(Metric):
    __tablename__ = "create_course_metrics"

    username = Column(String(15), nullable=False)
    graph_id = Column(String(24))

    def __repr__(self):
        return f"<CreateCourseMetric(username='{self.username}', graph_id='{self.graph_id}', date_time={self.date_time}, exec_time={self.exec_time}, status='{self.status}')>"


class GetGraphsMetric(Metric):
    __tablename__ = "get_graphs_metrics"

    graph_ids = Column(ARRAY(String(24)))

    def __repr__(self):
        return f"<GetGraphsMetric(graph_ids={self.graph_ids}, date_time={self.date_time}, exec_time={self.exec_time}, status='{self.status}')>"


class GetTopicMetric(Metric):
    __tablename__ = "get_topic_metrics"

    topic_id = Column(String(24))

    def __repr__(self):
        return f"<GetTopicMetric(topic_id='{self.topic_id}', date_time={self.date_time}, exec_time={self.exec_time}, status='{self.status}')>"


class GetGraphsPreviewMetric(Metric):
    __tablename__ = "get_graphs_preview_metrics"

    graph_ids = Column(ARRAY(String(24)))

    def __repr__(self):
        return f"<GetGraphsPreviewMetric(graph_ids={self.graph_ids}, date_time={self.date_time}, exec_time={self.exec_time}, status='{self.status}')>"


async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
