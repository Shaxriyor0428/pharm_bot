from typing import List, Dict, Any, Optional
from bot.config.database import get_conn


async def fetch_dict(query: str, *args) -> List[Dict[str, Any]]:
    """Bir nechta row qaytaradi"""
    async with get_conn() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(row) for row in rows]


async def fetchrow_dict(query: str, *args) -> Optional[Dict[str, Any]]:
    """Bitta row qaytaradi"""
    async with get_conn() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None


async def execute(query: str, *args) -> Dict[str, Any]:
    async with get_conn() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else {}


async def executemany(query: str, args_list: List[tuple]) -> None:
    """Ko‘p ma’lumotni birdaniga insert qilish"""
    async with get_conn() as conn:
        await conn.executemany(query, args_list)
