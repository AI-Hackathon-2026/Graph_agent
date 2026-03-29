import asyncio

from metrics import MetricsCollector
from sqlalchemy.ext.asyncio import create_async_engine

from agent.config import PostgresSettings
from agent.kafka_handler import kafka_handler
from agent.sql_models import init_db

if __name__ == "main":
    psg_engine = create_async_engine(PostgresSettings.URL)
    metrics_collector = MetricsCollector(psg_engine)

    asyncio.run(kafka_handler.consume())
    asyncio.run(init_db(psg_engine))
    asyncio.run(metrics_collector.write_metrics())
