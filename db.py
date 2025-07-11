import os
import asyncpg
import asyncio

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

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

async def add_user(pool, telegram_id: int, username: str = None):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (telegram_id, username)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO NOTHING;
        """, telegram_id, username)

async def get_user(pool, telegram_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1;", telegram_id)
import asyncpg
import os

async def init_db():
    conn = await asyncpg.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432))
    )
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS bets (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            match TEXT,
            odds FLOAT,
            timestamp TIMESTAMP DEFAULT NOW()
        );
    """)
    await conn.close()
