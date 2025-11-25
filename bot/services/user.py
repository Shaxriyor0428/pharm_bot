from bot.helpers import fetch_dict, fetchrow_dict


# async def get_user_by_chat(chat_id):
#     """Berilgan chat_id bo‘yicha foydalanuvchini qaytaradi."""
#     return await fetchrow_dict(
#         "SELECT * FROM users WHERE chat_id = $1",
#         chat_id
#     )
#
# async def get_all_admins():
#     """Admin va superadmin foydalanuvchilarni qaytaradi."""
#     return await fetch_dict(
#         "SELECT * FROM users WHERE role = ANY($1) AND status = $2",
#         ["admin", "superadmin"],
#         "accepted"
#     )


import httpx
BASE_URL = "https://pharm-backend.shaxriyorbek.uz"

async def get_user_by_chat(chat_id: int):
    """Berilgan chat_id bo‘yicha foydalanuvchini qaytaradi."""
    url = f"{BASE_URL}/users/by-chat/{chat_id}/?chat_id={chat_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    return response.json()

async def get_all_admins(chat_id):
    """Admin va superadmin foydalanuvchilarni qaytaradi."""
    url = f"{BASE_URL}/users/get_all_admins/?chat_id={chat_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    # JSON formatdagi list qaytaramiz
    return response.json()
