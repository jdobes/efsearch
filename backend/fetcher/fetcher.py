import asyncio
from datetime import datetime
import json
import logging
import re
import signal
import time

import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from nats.aio.client import Client

from common.config import NATS_HOST, NATS_PAGES_TOPIC, EF_BASE_URL, FETCHER_TASKS, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, \
    POSTGRES_DB
from common.logging import init_logging, get_logger

LOGGER = get_logger(__name__)

NC = Client()
SESSION = aiohttp.ClientSession()
SEMAPHORE = asyncio.Semaphore(FETCHER_TASKS)
RUNTIME = {}

URL_PREFIX = {"article": "/clanky/-", "match": "/serie-a/reportaz/-"}
FORUM_SUFIX = "/?forum=1"
ARTICLE_CLASS_NAME = {"article": "article", "match": "matchmain"}
PAGE_TYPE_TO_ID = {}
ACCOUNT_ID_TO_DB_ID = {}

DATETIME_FORMAT = "%d.%m.%Y %H:%M"

RE_COMPILE_URL = re.compile(r'<a [^<]+>([^<]+)</a>')

async def terminate(_, loop):
    """Trigger shutdown."""
    LOGGER.info("Signal received, stopping.")
    await SESSION.close()
    await RUNTIME["db_pool"].close()
    await NC.drain()
    loop.stop()


def preprocess_text(text):
    text = text.replace('<img class="smile" src="/res/img/smiles/biggrin.gif"/>', "::biggrin::")
    text = text.replace('<img class="smile" src="/res/img/smiles/confused.gif"/>', "::confused::")
    text = text.replace('<img class="smile" src="/res/img/smiles/cool.gif"/>', "::cool::")
    text = text.replace('<img class="smile" src="/res/img/smiles/cry.gif"/>', "::cry::")
    text = text.replace('<img class="smile" src="/res/img/smiles/eek.gif"/>', "::eek::")
    text = text.replace('<img class="smile" src="/res/img/smiles/evil.gif"/>', "::evil::")
    text = text.replace('<img class="smile" src="/res/img/smiles/frown.gif"/>', "::frown::")
    text = text.replace('<img class="smile" src="/res/img/smiles/lol.gif"/>', "::lol::")
    text = text.replace('<img class="smile" src="/res/img/smiles/mad.gif"/>', "::mad::")
    text = text.replace('<img class="smile" src="/res/img/smiles/neutral.gif"/>', "::neutral::")
    text = text.replace('<img class="smile" src="/res/img/smiles/razz.gif"/>', "::razz::")
    text = text.replace('<img class="smile" src="/res/img/smiles/redface.gif"/>', "::redface::")
    text = text.replace('<img class="smile" src="/res/img/smiles/rolleyes.gif"/>', "::rolleyes::")
    text = text.replace('<img class="smile" src="/res/img/smiles/smile.gif"/>', "::smile::")
    text = text.replace('<img class="smile" src="/res/img/smiles/wink.gif"/>', "::wink::")
    text = text.replace('<img class="smile" src="/res/img/smiles/talking.gif"/>', "::talking::")
    text = text.replace('<img class="smile" src="/res/img/smiles/spew.gif"/>', "::spew::")
    text = text.replace('<img class="smile" src="/res/img/smiles/facepalm.gif"/>', "::facepalm::")
    text = text.replace('<img class="smile" src="/res/img/smiles/thumbsup.gif"/>', "::thumbsup::")
    text = text.replace('<img class="smile" src="/res/img/smiles/thumbsdown.gif"/>', "::thumbsdown::")
    text = text.replace('<br/>', "\n")
    text = RE_COMPILE_URL.sub(r'\1', text)
    return text


def parse_page(page, page_category, ef_id):
    data = {}
    article = page.find('div', attrs={'class': ARTICLE_CLASS_NAME[page_category]})
    forum = page.find('div', attrs={'class': 'forum'})
    # Page exists
    if article and forum:
        data['name'] = article.h2.text
        data['created'] = article.find('div', attrs={'class': 'date'}).text[0:16]
        # Check date format
        data['created'] = data['created'].replace('CET', '').replace('?', '00:00').strip()
        if data['created'] == "00.00.0000 00:00":
            data['created'] = "01.01.1970 00:00"

        data['forum'] = []
        for post in forum.findAll('div', attrs={'class': 'post'}):
            comment = {}
            comment['id'] = int(post.get('id')[1:])

            parent = None
            parent_link = post.find('div', attrs={'class': 'parentlink'})
            if parent_link:
                parent = int(parent_link.a['onclick'].rsplit('(', 1)[1][:-2])
            comment['parent_id'] = parent

            user_link = post.find('a', attrs={'class': 'name'})
            # User must be registered
            if user_link and user_link.text:
                comment['account_id'] = int(user_link.get('onclick').split()[1][:-1])
                comment['account'] = user_link.text
            else:
                comment['account_id'] = 0
                comment['account'] = ""
            comment['created'] = post.find('div', attrs={'class': 'time'}).text
            # Check date format
            comment['body'] = preprocess_text(post.find('div', attrs={'class': 'text'}).decode_contents())

            data['forum'].append(comment)
    else:
        LOGGER.warning(f"Page is invalid: {page_category}/{ef_id}")
    return data


async def store_accounts(missing_accounts):
    async with asyncio.Semaphore(1):
        rows = None
        async with RUNTIME["db_pool"].acquire() as conn:
            async with conn.transaction():
                rows = await conn.fetch("""
                    INSERT INTO account (ef_id, name)
                    (SELECT r.ef_id, r.name FROM unnest($1::account[]) as r)
                    ON CONFLICT DO NOTHING
                    RETURNING id, ef_id
                """, sorted(missing_accounts, key=lambda x: x[1]))
        if rows:
            for row in rows:
                ACCOUNT_ID_TO_DB_ID[row["ef_id"]] = row["id"]
            LOGGER.info(f"Stored new accounts: {len(rows)}")


async def store_page(data, page_category, ef_id):
    async with RUNTIME["db_pool"].acquire() as conn:
        async with conn.transaction():
            page_id = await conn.fetchval("SELECT id FROM page WHERE page_category_id = $1 AND ef_id = $2 FOR UPDATE", PAGE_TYPE_TO_ID[page_category], ef_id)  # acquire lock
            page_date = datetime.strptime(data['created'], DATETIME_FORMAT)
            await conn.execute("""
                UPDATE page SET
                    created = $2,
                    name = $3,
                    last_sync = now()
                WHERE id = $1
            """, page_id, page_date, data["name"])

            existing_ef_ids = set()
            rows = await conn.fetch("SELECT ef_id from post WHERE page_id = $1", page_id)
            for row in rows:
                existing_ef_ids.add(row["ef_id"])
            
            # handle accounts
            missing_accounts = set()
            for comment in data["forum"]:
                if comment["id"] in existing_ef_ids:
                    continue
                if comment["account_id"] not in ACCOUNT_ID_TO_DB_ID:
                    # None because - https://stackoverflow.com/questions/43739123/best-way-to-insert-multiple-rows-with-asyncpg
                    missing_accounts.add((None, comment["account_id"], comment["account"]))

            # lookup accounts
            if missing_accounts:
                await store_accounts(missing_accounts)

            # handle comments
            missing_comments = []
            for comment in data["forum"]:
                if comment["id"] in existing_ef_ids:
                    continue
                comment_date = datetime.strptime(comment['created'], DATETIME_FORMAT)
                missing_comments.append((None, comment["id"], comment_date, page_id, comment["parent_id"], ACCOUNT_ID_TO_DB_ID[comment["account_id"]], comment["body"], 0))

            if missing_comments:
                # FIXME: Avoiding duplicate posts by ON-CONFLICT-DO-NOTHING, in future introduce discussion_id and do not do that
                await conn.execute("""
                    INSERT INTO post (ef_id, created, page_id, parent_ef_id, account_id, body)
                    (SELECT r.ef_id, r.created, r.page_id, r.parent_ef_id, r.account_id, r.body FROM unnest($1::post[]) as r)
                    ON CONFLICT DO NOTHING
                """, sorted(missing_comments, key=lambda x: x[1]))

                await conn.execute("SELECT update_funny_ranking($1)", page_id)

        LOGGER.info(f"Stored page: {page_category}/{ef_id} - {len(missing_comments)} missing comments")


async def sync_page(page_category, ef_id):
    async with SEMAPHORE:
        page_url = f"{EF_BASE_URL}{URL_PREFIX[page_category]}{ef_id}{FORUM_SUFIX}"
        tries = 0
        html = None
        for i in range(4):
            try:
                async with SESSION.get(page_url) as response:
                    if response.status == 200:
                        LOGGER.info(f"Fetched page: {page_category}/{ef_id} - HTTP {response.status}")
                        html = await response.text()
                    else:
                        LOGGER.warning(f"Unable to fetch page: {page_category}/{ef_id} - HTTP {response.status}")
                    break
            except aiohttp.client_exceptions.ServerDisconnectedError:
                tries += 1
                if tries >= 4:
                    raise
                else:
                    LOGGER.warning(f"Retrying fetch of page: {page_category}/{ef_id}")
        if html:
            page = BeautifulSoup(html, 'lxml')
            data = parse_page(page, page_category, ef_id)
            if data:
                await store_page(data, page_category, ef_id)


async def prepare_page_type_to_id_cache():
    async with RUNTIME["db_pool"].acquire() as conn:
        rows = await conn.fetch("SELECT id, name FROM page_category")
        for row in rows:
            PAGE_TYPE_TO_ID[row["name"]] = row["id"]


async def prepare_account_id_cache():
    async with RUNTIME["db_pool"].acquire() as conn:
        rows = await conn.fetch("SELECT id, ef_id FROM account")
        for row in rows:
            ACCOUNT_ID_TO_DB_ID[row["ef_id"]] = row["id"]


async def message_handler(msg):
    pages = json.loads(msg.data.decode())
    for page in pages:
        async with SEMAPHORE:
            asyncio.get_event_loop().create_task(sync_page(page["page_category"], int(page["ef_id"])))
            LOGGER.debug(f"Task for page created: {page}")


async def run(loop):
    RUNTIME["db_pool"] = await asyncpg.create_pool(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}",
                                                   min_size=FETCHER_TASKS*2, max_size=FETCHER_TASKS*2)
    await prepare_page_type_to_id_cache()
    await prepare_account_id_cache()
    await NC.connect(servers=[NATS_HOST], loop=loop)
    await NC.subscribe(NATS_PAGES_TOPIC, cb=message_handler)
    LOGGER.info(f"Connected to {NATS_HOST}, listening on {NATS_PAGES_TOPIC} topic...")


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
