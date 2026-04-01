import asyncio

from agent.metrics import metrics_collector, psg_engine
from agent.sql_models import init_db


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
