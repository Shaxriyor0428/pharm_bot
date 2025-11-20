from bot.config.database import get_conn

async def create_tables():
    enable_uuid = "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

    create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username VARCHAR(150) UNIQUE,
            email VARCHAR(150),
            status VARCHAR(20) NOT NULL CHECK (status IN ('accepted', 'pending', 'rejected'))
                DEFAULT 'pending',
            role VARCHAR(20) NOT NULL CHECK (role IN ('seller', 'admin', 'superadmin'))
                DEFAULT 'seller',
            region_id UUID NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
            password VARCHAR(255),
            chat_id BIGINT UNIQUE,
            first_name VARCHAR(150),
            last_name VARCHAR(150),
            is_superuser BOOLEAN DEFAULT false,
            is_staff BOOLEAN DEFAULT false,
            is_active BOOLEAN DEFAULT true,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    create_geo_locations_table = """
        CREATE TABLE IF NOT EXISTS user_geo_locations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            lat DOUBLE PRECISION NOT NULL,
            lon DOUBLE PRECISION NOT NULL,
            video_id VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    async with get_conn() as conn:
        await conn.execute(enable_uuid)
        await conn.execute(create_users_table)
        await conn.execute(create_geo_locations_table)
