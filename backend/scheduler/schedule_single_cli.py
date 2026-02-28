import asyncio
import json
import signal
import sys

from nats.aio.client import Client

from backend.common.config import NATS_HOST, NATS_PAGES_TOPIC
from backend.common.logging import init_logging, get_logger

LOGGER = get_logger(__name__)

NC = Client()


async def terminate(_, loop):
    """Trigger shutdown."""
    LOGGER.info("Signal received, stopping.")
    loop.stop()


async def run(loop, page_category, ef_id):
    await NC.connect(servers=[NATS_HOST])
    chunk = [{"page_category": page_category, "ef_id": ef_id}]
    await NC.publish(NATS_PAGES_TOPIC, json.dumps(chunk).encode())
    LOGGER.info("Published.")
    await NC.close()
    await terminate(None, loop)


def main(page_category, ef_id):
    init_logging()
    loop = asyncio.get_event_loop()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sig in signals:
        loop.add_signal_handler(
            sig, lambda sig=sig: loop.create_task(terminate(sig, loop)))

    loop.run_until_complete(run(loop, page_category, ef_id))
    loop.run_forever()
    loop.close()
    LOGGER.info("Stopped.")


if __name__ == "__main__":
    # argv[1] - article/match
    # argv[2] - 567890
    main(sys.argv[1], sys.argv[2])
