from typing import Any, Optional

from bot.services.api import request_json


async def get_user_by_chat(chat_id: int) -> Optional[dict[str, Any]]:
    """
    Berilgan chat_id bo'yicha foydalanuvchini qaytaradi (status'idan qat'i nazar).
    Ro'yxatdan o'tmagan bo'lsa None.

    /users/profile/ endpointi permission talab qilmaydi, shuning uchun
    pending/rejected userlar uchun ham ma'lumot qaytaradi — bot shu orqali
    "tasdiqlanmagan" holatini alohida ko'rsata oladi.
    """
    status, body = await request_json("GET", "/users/profile/", params={"chat_id": chat_id})
    if status == 200 and isinstance(body, dict):
        return body
    return None


async def get_all_admins(chat_id: int) -> list[dict[str, Any]]:
    """Admin va superadmin foydalanuvchilarni qaytaradi (xato bo'lsa bo'sh ro'yxat)."""
    status, body = await request_json("GET", "/users/get_all_admins/", params={"chat_id": chat_id})
    if status == 200 and isinstance(body, list):
        return body
    return []
