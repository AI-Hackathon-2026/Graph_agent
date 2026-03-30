import asyncio

from metrics import LoadMonitor, MetricsCollector
from sqlalchemy.ext.asyncio import create_async_engine

from agent.config import postgres_settings
from agent.sql_models import init_db

psg_engine = create_async_engine(postgres_settings.URL)
load_monitor = LoadMonitor()
metrics_collector = MetricsCollector(psg_engine, load_monitor)


async def main():
    from agent.kafka_handler import KafkaHandler

    kafka_handler = KafkaHandler()

    await asyncio.gather(
        init_db(psg_engine),
        metrics_collector.write_metrics(),
        kafka_handler.consume(),
        metrics_collector.load_monitor.load_check(),
    )
    await kafka_handler.consumer.stop()
    await kafka_handler.producer.stop()


if __name__ == "__main__":
    asyncio.run(main())
