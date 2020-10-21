import asyncio
import asyncpg
from asyncpg.exceptions import UndefinedTableError
import os

from common.logging import init_logging, get_logger

LOGGER = get_logger(__name__)

POSTGRES_USER = os.getenv("POSTGRES_USER", "unknown")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "unknown")
POSTGRES_DB = os.getenv("POSTGRES_DB", "unknown")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "unknown")


async def main():
    init_logging()

    conn = await asyncpg.connect(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}")

    try:
        db_version = await conn.fetchval("SELECT value FROM db_version")
    except UndefinedTableError:
        db_version = None

    if db_version is None:
        LOGGER.info("Initializing DB...")
        async with conn.transaction():
            await conn.execute("""
                CREATE TABLE db_version (
                    key TEXT,
                    value INTEGER
                )
            """)
            await conn.execute("INSERT INTO db_version (key, value) VALUES ('db_version', 0)")
            LOGGER.info("Created table: db_version")

            await conn.execute("""
                CREATE TABLE page_category (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            await conn.execute("INSERT INTO page_category (name) VALUES ('article'), ('match')")
            LOGGER.info("Created table: page_category")

            await conn.execute("""
                CREATE TABLE page (
                    id SERIAL PRIMARY KEY,
                    ef_id INTEGER UNIQUE NOT NULL,
                    page_category_id INTEGER REFERENCES page_category (id) NOT NULL,
                    created TIMESTAMP WITH TIME ZONE,
                    views INTEGER,
                    name TEXT NOT NULL,
                    last_sync TIMESTAMP WITH TIME ZONE
                )
            """)
            LOGGER.info("Created table: page")

            await conn.execute("""
                CREATE TABLE account (
                    id SERIAL PRIMARY KEY,
                    ef_id INTEGER UNIQUE NOT NULL,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            LOGGER.info("Created table: account")

            await conn.execute("""
                CREATE TABLE post (
                    id SERIAL PRIMARY KEY,
                    ef_id INTEGER UNIQUE NOT NULL,
                    created TIMESTAMP WITH TIME ZONE,
                    page_id INTEGER REFERENCES page (id) NOT NULL,
                    parent_ef_id INTEGER,
                    account_id INTEGER REFERENCES account (id) NOT NULL,
                    body TEXT,
                    funny_ranking INTEGER NOT NULL DEFAULT 0
                )
            """)
            LOGGER.info("Created table: post")

            await conn.execute("""
                CREATE MATERIALIZED VIEW post_cache AS
                    (SELECT a.name, count(*)
                    FROM post p INNER JOIN
                         account a ON a.id = p.account_id
                    WHERE a.name != ''
                    GROUP BY a.name)
                    UNION ALL
                    (SELECT '', COUNT(*) FROM post)
            """)
            LOGGER.info("Created materialized view: post_cache")

        LOGGER.info("DB initialization finished.")
    else:
        LOGGER.info("DB already initialized.")

    await conn.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
