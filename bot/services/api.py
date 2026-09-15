"""
Backend REST API bilan ishlash uchun umumiy yordamchi.

Barcha so'rovlar shu yerdan o'tadi: bitta AsyncClient, timeout va
status-code tekshiruvi. Muvaffaqiyatsiz javoblar exception o'rniga
None qaytaradi — handlerlar o'zi foydalanuvchiga tushunarli xabar beradi.
"""
import logging
from typing import Any, Optional

import httpx

from bot.config.env import BACKEND_URL, HTTP_TIMEOUT

logger = logging.getLogger(__name__)

_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=HTTP_TIMEOUT)
    return _client


async def close_client() -> None:
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
    _client = None


async def request_json(method: str, path: str, **kwargs) -> tuple[int, Any]:
    """
    (status_code, json_body) qaytaradi. Tarmoq xatosi bo'lsa (0, None).
    JSON bo'lmagan javobda body None bo'ladi.
    """
    try:
        response = await get_client().request(method, path, **kwargs)
    except httpx.HTTPError as exc:
        logger.warning("Backend so'rovida xato: %s %s -> %s", method, path, exc)
        return 0, None

    try:
        body = response.json()
    except ValueError:
        body = None

    if response.status_code >= 400:
        logger.info("Backend %s %s -> %s %s", method, path, response.status_code, body)

    return response.status_code, body
