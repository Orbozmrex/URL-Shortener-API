import aiosqlite
import secrets

async def init_db():
    async with aiosqlite.connect('database.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS urls (token TEXT UNIQUE PRIMARY KEY, url TEXT NOT NULL)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS url_stats (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT NOT NULL, last_visited DATETIME, visits INTEGER NOT NULL, FOREIGN KEY(token) REFERENCES urls(token))''')
        await db.execute('''CREATE INDEX IF NOT EXISTS idx_token on urls (token)''')
        await db.commit()

async def get_url(token: str) -> str | None:
    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute('''SELECT url FROM urls WHERE token = ?''', (token,))
            url = await cursor.fetchone()
            return url[0] if url else None

async def add_url(url: str):
    token = secrets.token_urlsafe(10)
    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute('''INSERT INTO urls (token, url) VALUES (?, ?)''', (token, url))
            await db.commit()
            return token