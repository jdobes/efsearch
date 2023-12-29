import asyncio
from datetime import datetime
import json
import signal

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncpg
from bs4 import BeautifulSoup
from nats.aio.client import Client

from backend.common.config import NATS_HOST, NATS_PAGES_TOPIC, EF_BASE_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, \
    POSTGRES_HOST, QUEUE_NEW_PAGES_INTERVAL, REFRESH_POST_CACHE_INTERVAL, EF_USER, EF_PASSWORD, EF_LOGIN_URL
from backend.common.logging import init_logging, get_logger

LOGGER = get_logger(__name__)

NC = Client()
SESSION = aiohttp.ClientSession()
RUNTIME = {}

PAGE_TYPE_TO_ID = {}
ID_TO_PAGE_TYPE = {}


async def terminate(_, loop):
    """Trigger shutdown."""
    LOGGER.info("Signal received, stopping.")
    await SESSION.close()
    await RUNTIME["db_pool"].close()
    await NC.drain()
    loop.stop()


async def prepare_page_type_to_id_cache():
    async with RUNTIME["db_pool"].acquire() as conn:
        rows = await conn.fetch("SELECT id, name FROM page_category")
        for row in rows:
            PAGE_TYPE_TO_ID[row["name"]] = row["id"]
            ID_TO_PAGE_TYPE[row["id"]] = row["name"]


async def login():
    payload = {'login': EF_USER, 'pass': EF_PASSWORD}
    async with SESSION.post(EF_LOGIN_URL, data=payload) as response:
        LOGGER.info(f"Login as {EF_USER}:{EF_PASSWORD} - HTTP {response.status}")


async def get_top_ids_web():
    """Get and return current last id of article"""
    page_url = f"{EF_BASE_URL}"
    result = {}
    async with SESSION.get(page_url) as response:
        if response.status == 200:
            LOGGER.info(f"Fetched page: {page_url} - HTTP {response.status}")
            html = await response.text()
            page = BeautifulSoup(html, 'lxml')
            links = page.findAll('a')
            ids = {"article": [], "match": []}
            for link in links:
                page_category = None
                if "/clanky/" in link['href']:
                    page_category = "article"
                elif "/preview/" in link['href'] or "/reportaz/" in link['href']:
                    page_category = "match"

                if page_category:
                    parts = link['href'].split('-')
                    try:
                        number = int(parts[-1].replace('/', ''))
                        ids[page_category].append(number)
                    except ValueError:
                        continue
            result["article"] = max(ids["article"])
            result["match"] = max(ids["match"])
        else:
            LOGGER.warning(f"Unable to fetch page: {page_url} - HTTP {response.status}")

    return result


async def queue_new_pages():
    top_ids_web = await get_top_ids_web()
    async with RUNTIME["db_pool"].acquire() as conn:
        rows = await conn.fetch("SELECT pc.name, max(p.ef_id) FROM page p JOIN page_category pc ON p.page_category_id = pc.id GROUP BY pc.name")
        top_ids_db = {}
        for row in rows:
            top_ids_db[row["name"]] = row["max"]
        to_insert = []
        for page_category in ["article", "match"]:
            top_id_web = top_ids_web[page_category]
            top_id_db = top_ids_db.get(page_category, 0)
            if top_id_web > top_id_db:
                LOGGER.info(f"Missing pages: {page_category}/{top_id_db+1}-{top_id_web}")
                for idx in range(top_id_web, top_id_db, -1):
                    to_insert.append((None, idx, PAGE_TYPE_TO_ID[page_category], None, None, None))
        await conn.execute("""
            INSERT INTO page (page_category_id, ef_id)
            (SELECT r.page_category_id, r.ef_id FROM unnest($1::page[]) as r)
        """, to_insert)
    LOGGER.info(f"Inserted {len(to_insert)} new pages")

    #await login()
    # subscribe all
    # FIXME: ugly, move to function and parametrize...
    chunk = []
    for row in to_insert:
        chunk.append({"page_category": ID_TO_PAGE_TYPE[row[2]], "ef_id": str(row[1])})
        if len(chunk) % 10000 == 0:
            await NC.publish(NATS_PAGES_TOPIC, json.dumps(chunk).encode())
            LOGGER.info("Scheduled fetch of 10000 pages.")
            chunk = []
    if chunk:
        await NC.publish(NATS_PAGES_TOPIC, json.dumps(chunk).encode())
        LOGGER.info(f"Scheduled fetch of {len(chunk)} pages.")


async def queue_unsynced_pages():
    async with RUNTIME["db_pool"].acquire() as conn:
        rows = await conn.fetch("SELECT pc.name, p.ef_id FROM page p JOIN page_category pc ON p.page_category_id = pc.id WHERE p.last_sync IS NULL ORDER BY pc.name, p.ef_id DESC")
    if rows:
        chunk = []
        for row in rows:
            chunk.append({"page_category": row["name"], "ef_id": str(row["ef_id"])})
            if len(chunk) % 10000 == 0:
                await NC.publish(NATS_PAGES_TOPIC, json.dumps(chunk).encode())
                LOGGER.info("Scheduled fetch of 10000 pages.")
                chunk = []
        if chunk:
            await NC.publish(NATS_PAGES_TOPIC, json.dumps(chunk).encode())
            LOGGER.info(f"Scheduled fetch of {len(chunk)} pages.")


async def refresh_post_cache():
    async with RUNTIME["db_pool"].acquire() as conn:
        await conn.execute("REFRESH MATERIALIZED VIEW post_cache")
    LOGGER.info("Materialized view post_cache refreshed")


async def init(loop):
    RUNTIME["db_pool"] = await asyncpg.create_pool(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}",
                                                   min_size=2, max_size=2)
    await prepare_page_type_to_id_cache()
    await NC.connect(servers=[NATS_HOST], loop=loop)


def main():
    init_logging()
    loop = asyncio.get_event_loop()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sig in signals:
        loop.add_signal_handler(
            sig, lambda sig=sig: loop.create_task(terminate(sig, loop)))

    loop.run_until_complete(init(loop))
    loop.run_until_complete(queue_unsynced_pages())

    scheduler = AsyncIOScheduler()
    scheduler.add_job(queue_new_pages, "interval", seconds=QUEUE_NEW_PAGES_INTERVAL, next_run_time=datetime.now())
    scheduler.add_job(refresh_post_cache, "interval", seconds=REFRESH_POST_CACHE_INTERVAL, next_run_time=datetime.now())
    scheduler.start()

    loop.run_forever()
    loop.close()
    LOGGER.info("Stopped.")


if __name__ == "__main__":
    main()
