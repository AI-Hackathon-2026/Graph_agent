import asyncio

from agent.metrics import metrics_collector, psg_engine
from agent.sql_models import init_db


async def main():
    from agent.kafka_handler import kafka_handler

    tasks = [
        asyncio.create_task(init_db(psg_engine)),
        metrics_collector.write_metrics(),
        kafka_handler.consume(),
        metrics_collector.load_monitor.load_check(),
    ]
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        pass
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
