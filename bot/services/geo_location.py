from bot.helpers import execute

# async def create_geo_location(lat, lon, video_id, user_id):
#     """Yangi geo location yaratadi va uni qaytaradi."""
#     query = """
#         INSERT INTO user_geo_locations (
#             latitude,
#             longitude,
#             video_id,
#             user_id
#         )
#         VALUES ($1, $2, $3, $4)
#         RETURNING *;
#     """
#
#     return await execute(query, lat, lon, video_id, user_id)

import httpx

BASE_URL = "https://pharm-backend.shaxriyorbek.uz"

async def create_geo_location(lat, lon, video_id, chat_id):
    """Yangi geo location yaratadi va uni qaytaradi."""
    url = f"{BASE_URL}/users/create_geo_location/"

    payload = {
        "lat": lat,
        "lon": lon,
        "video_id": video_id,
        "chat_id": chat_id
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)

    return response.json()
