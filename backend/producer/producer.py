import asyncio
import json
import logging
import signal

from nats.aio.client import Client

from common.constants import NATS_HOST
from common.logging import init_logging, get_logger

LOGGER = get_logger(__name__)

NC = Client()


async def terminate(_, loop):
    """Trigger shutdown."""
    LOGGER.info("Signal received, stopping.")
    loop.stop()


async def run(loop):
    await NC.connect(servers=[NATS_HOST], loop=loop)
    await asyncio.sleep(10)
    for i in range(10):
        await NC.publish("updates", json.dumps({"symbol": "GOOG", "price": 1200 }).encode())
    LOGGER.info("Published 10 msgs.")
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
