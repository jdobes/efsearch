import asyncio
import json
import logging
import signal

from nats.aio.client import Client

from common.config import NATS_HOST, NATS_PAGES_TOPIC
from common.logging import init_logging, get_logger

LOGGER = get_logger(__name__)

NC = Client()


async def terminate(_, loop):
    """Trigger shutdown."""
    LOGGER.info("Signal received, stopping.")
    await SESSION.close()
    loop.stop()


async def run(loop):
    await NC.connect(servers=[NATS_HOST], loop=loop)
    while True:
        await NC.publish(NATS_PAGES_TOPIC, json.dumps([{"page_category": "article", "ef_id": "481777"},{"page_category": "match", "ef_id": "665036"}]).encode())
        LOGGER.info("Scheduled fetch of 1 page.")
        await asyncio.sleep(10)
    await NC.close()


def main():
    init_logging()
    loop = asyncio.get_event_loop()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sig in signals:
        loop.add_signal_handler(
            sig, lambda sig=sig: loop.create_task(terminate(sig, loop)))

    loop.run_until_complete(run(loop))
    loop.run_forever()
    loop.close()
    LOGGER.info("Stopped.")


if __name__ == "__main__":
    main()
