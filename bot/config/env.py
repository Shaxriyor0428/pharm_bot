from decouple import config

BOT_TOKEN = config("BOT_TOKEN")
DB_CONFIG = {
    "user": config("DB_USER"),
    "password": config("DB_PASSWORD"),
    "database": config("DB_NAME"),
    "host": config("DB_HOST"),
    "port": config("DB_PORT", cast=int),
}