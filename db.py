import aiosqlite
import logging

import aiosqlite
import logging
import os

# Use a specific path for the database if provided (useful for Railway Volumes)
# Example: RAILWAY_VOLUME_MOUNT_PATH could be /app/data
DB_PATH = os.getenv("DB_PATH", "hafiz_bot.db")
DB_NAME = DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                gender TEXT,
                status TEXT DEFAULT 'started',
                verified_surah_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Attempt to add column if it doesn't exist (migration)
        try:
            await db.execute("ALTER TABLE users ADD COLUMN verified_surah_count INTEGER DEFAULT 0")
        except Exception:
            pass # Column likely exists
            
        await db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        await db.commit()

async def add_user(user_id, username, full_name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, full_name, status)
            VALUES (?, ?, ?, 'started')
        """, (user_id, username, full_name))
        await db.commit()

async def update_user_gender(user_id, gender):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET gender = ? WHERE user_id = ?", (gender, user_id))
        await db.commit()

async def update_user_status(user_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
        await db.commit()

async def set_verified_surah_count(user_id, count):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET verified_surah_count = ? WHERE user_id = ?", (count, user_id))
        await db.commit()

async def add_submission(user_id, file_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO submissions (user_id, file_id) VALUES (?, ?)", (user_id, file_id))
        await db.commit()

async def get_user_submissions(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT file_id FROM submissions WHERE user_id = ?", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            total = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE status = 'pending'") as cursor:
            pending = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE status = 'approved'") as cursor:
            approved = (await cursor.fetchone())[0]
        return total, pending, approved

async def get_users_by_gender(gender):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        # Order by verified_surah_count DESC for winner selection
        async with db.execute("""
            SELECT * FROM users 
            WHERE gender = ? AND status = 'approved'
            ORDER BY verified_surah_count DESC
        """, (gender,)) as cursor:
            return await cursor.fetchall()

async def delete_user_data(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM submissions WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.commit()

async def reset_all_data():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM submissions")
        await db.execute("DELETE FROM users")
        await db.commit()


