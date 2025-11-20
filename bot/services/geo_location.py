from bot.helpers import execute

async def create_geo_location(lat, lon, video_id, user_id):
    """Yangi geo location yaratadi va uni qaytaradi."""
    query = """
        INSERT INTO user_geo_locations (
            latitude,
            longitude,
            video_id,
            user_id
        )
        VALUES ($1, $2, $3, $4)
        RETURNING *;
    """

    return await execute(query, lat, lon, video_id, user_id)
