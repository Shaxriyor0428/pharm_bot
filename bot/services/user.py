from bot.helpers import fetch_dict, fetchrow_dict


async def get_user_by_chat(chat_id):
    """Berilgan chat_id bo‘yicha foydalanuvchini qaytaradi."""
    return await fetchrow_dict(
        "SELECT * FROM users WHERE chat_id = $1",
        chat_id
    )

async def get_all_admins():
    """Admin va superadmin foydalanuvchilarni qaytaradi."""
    return await fetch_dict(
        "SELECT * FROM users WHERE role = ANY($1) AND status = $2",
        ["admin", "superadmin"],
        "accepted"
    )
