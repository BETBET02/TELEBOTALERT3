import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Luo yhteyspooli (pool = useita yhteyksiä hallitusti)
async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

# Alustetaan tietokanta (luodaan taulut jos puuttuvat)
async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE,
                username TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                match TEXT,
                odds FLOAT,
                timestamp TIMESTAMP DEFAULT NOW()
            );
        """)

# Lisää käyttäjä
async def add_user(pool, telegram_id: int, username: str = None):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (telegram_id, username)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO NOTHING;
        """, telegram_id, username)

# Hae käyttäjä ID:llä
async def get_user(pool, telegram_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            SELECT * FROM users WHERE telegram_id = $1;
        """, telegram_id)

# Lisää veto
async def add_bet(pool, user_id: int, match: str, odds: float):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO bets (user_id, match, odds)
            VALUES ($1, $2, $3);
        """, user_id, match, odds)
