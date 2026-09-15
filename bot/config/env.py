from decouple import config

BOT_TOKEN = config("BOT_TOKEN")

# Backend REST API manzili (oxirida / bo'lmasin)
BACKEND_URL = config("BACKEND_URL", default="https://pharm-backend.shaxriyorbek.uz").rstrip("/")

# HTTP so'rovlar uchun timeout (soniya)
HTTP_TIMEOUT = config("HTTP_TIMEOUT", default=15, cast=float)

# Legacy: bot avval to'g'ridan-to'g'ri Postgres'ga ulanardi (bot/config/database.py).
# Hozir barcha ma'lumotlar backend API orqali olinadi, shuning uchun DB_* ixtiyoriy.
DB_CONFIG = {
    "user": config("DB_USER", default=""),
    "password": config("DB_PASSWORD", default=""),
    "database": config("DB_NAME", default=""),
    "host": config("DB_HOST", default="localhost"),
    "port": config("DB_PORT", default=5432, cast=int),
}
