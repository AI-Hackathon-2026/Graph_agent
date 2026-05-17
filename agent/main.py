import asyncio

from agent.app import OrchestratorClient
from agent.kafka_handler import KafkaHandler
from agent.kafka_producer import KafkaProducer


async def main():
    producer = KafkaProducer()
    app = OrchestratorClient(producer)
    handler = KafkaHandler(app)

    tasks = [
        producer.start(),
        app.start_http_session(),
        handler.consume(),
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
