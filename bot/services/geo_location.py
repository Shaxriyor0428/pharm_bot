from typing import Any, Optional

from bot.services.api import request_json


async def create_geo_location(lat: float, lon: float, video_id: str, chat_id: int) -> Optional[dict[str, Any]]:
    """
    Yangi geo location yaratadi va yaratilgan yozuvni qaytaradi.
    Backend rad etsa (403 — tasdiqlanmagan user, 400 — noto'g'ri ma'lumot,
    tarmoq xatosi) None qaytaradi.
    """
    payload = {
        "lat": lat,
        "lon": lon,
        "video_id": video_id,
        "chat_id": chat_id,
    }
    status, body = await request_json("POST", "/users/create_geo_location/", json=payload)
    if status == 201 and isinstance(body, dict):
        return body
    return None
