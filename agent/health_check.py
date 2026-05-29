import sys

import aiohttp
from aiohttp import TCPConnector
from aiokafka import AIOKafkaProducer
from config import application_hosts_setting

connector = TCPConnector(limit=2000)
session = aiohttp.ClientSession(connector=connector)


async def check_kafka() -> bool:
    producer = AIOKafkaProducer(
        bootstrap_servers=application_hosts_setting.BOOTSTRAP_SERVER
    )
    try:
        await producer.start()
        return True
    except Exception:
        return False
    finally:
        await producer.stop()


async def check_orchestrator() -> bool:
    try:
        async with session.get(
            application_hosts_setting.ORCHESTRATOR_SERVER + "/health/readiness"
        ) as response:
            response.raise_for_status()
            return True
    except Exception:
        return False


def liveness_check():
    sys.exit(0)


async def readiness_check():
    kafka_ok = await check_kafka()
    orchestrator_ok = await check_orchestrator()
    sys.exit(0 if kafka_ok and orchestrator_ok else 1)
