import asyncpg
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from bot.config.env import DB_CONFIG
pool: Optional[asyncpg.Pool] = None
#
#
# async def init_db():
#     """Connection pool ochish"""
#     global pool
#     pool = await asyncpg.create_pool(**DB_CONFIG)
#
#
# async def close_db():
#     """Connection pool yopish"""
#     global pool
#     if pool:
#         await pool.close()
#

@asynccontextmanager
async def get_conn() -> AsyncGenerator[asyncpg.Connection, None]:
    async with pool.acquire() as conn:
        yield conn
