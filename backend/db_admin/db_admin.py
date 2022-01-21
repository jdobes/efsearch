import asyncio
import asyncpg
from asyncpg.exceptions import UndefinedTableError
import os

from backend.common.config import POSTGRES_DB, POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD
from backend.common.logging import init_logging, get_logger

LOGGER = get_logger(__name__)


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
            await conn.execute("CREATE EXTENSION pg_trgm")
            LOGGER.info("Created extension: pg_trgm")

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
                    id BIGSERIAL PRIMARY KEY,
                    ef_id INTEGER NOT NULL,
                    page_category_id INTEGER REFERENCES page_category (id) NOT NULL,
                    created TIMESTAMP,
                    name TEXT,
                    last_sync TIMESTAMP
                )
            """)
            LOGGER.info("Created table: page")

            await conn.execute("CREATE UNIQUE INDEX ON page(page_category_id, ef_id)")
            LOGGER.info("Created index on table: page")

            await conn.execute("""
                CREATE TABLE account (
                    id BIGSERIAL PRIMARY KEY,
                    ef_id INTEGER UNIQUE NOT NULL,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            LOGGER.info("Created table: account")

            await conn.execute("""
                CREATE TABLE post (
                    id BIGSERIAL PRIMARY KEY,
                    ef_id INTEGER UNIQUE NOT NULL,
                    created TIMESTAMP,
                    page_id INTEGER REFERENCES page (id) NOT NULL,
                    parent_ef_id INTEGER,
                    account_id INTEGER REFERENCES account (id) NOT NULL,
                    body TEXT,
                    funny_ranking INTEGER NOT NULL DEFAULT 0
                )
            """)
            LOGGER.info("Created table: post")

            await conn.execute("CREATE UNIQUE INDEX ON post(account_id, ef_id)")
            LOGGER.info("Created index on table: post")
            await conn.execute("CREATE INDEX ON post(created)")
            LOGGER.info("Created index on table: post")
            await conn.execute("CREATE INDEX ON post(page_id)")
            LOGGER.info("Created index on table: post")
            await conn.execute("CREATE INDEX ON post(parent_ef_id)")
            LOGGER.info("Created index on table: post")
            await conn.execute("CREATE INDEX ON post(account_id)")
            LOGGER.info("Created index on table: post")
            await conn.execute("CREATE INDEX ON post USING gin(body gin_trgm_ops)")
            LOGGER.info("Created index on table: post")
            await conn.execute("CREATE INDEX ON post(funny_ranking)")
            LOGGER.info("Created index on table: post")

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

            await conn.execute("CREATE UNIQUE INDEX ON post_cache(name)")
            LOGGER.info("Created index on materialized view: post_cache")
            await conn.execute("CREATE INDEX ON post_cache(count)")
            LOGGER.info("Created index on materialized view: post_cache")

            await conn.execute("""
                CREATE OR REPLACE FUNCTION update_funny_ranking(integer)
                RETURNS void AS $$
                    UPDATE post p1 SET funny_ranking = (
                        SELECT COUNT(*) FROM post p2
                        WHERE p2.parent_ef_id = p1.ef_id AND
                        (body ILIKE '%::biggrin::%' or body ILIKE '%::lol::%')
                    )
                    WHERE p1.page_id = $1
                $$
                LANGUAGE SQL
                VOLATILE;
            """)
            LOGGER.info("Created function: update_funny_ranking")

        LOGGER.info("DB initialization finished.")
    else:
        LOGGER.info("DB already initialized.")

    await conn.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
