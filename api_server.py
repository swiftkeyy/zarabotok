#!/usr/bin/env python3
"""
API сервер для получения данных пользователей
"""
import os
import asyncio
from aiohttp import web
from aiogram import Bot
from aiogram.types import BufferedInputFile

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import asyncpg
    DB_POOL = None
else:
    import aiosqlite
    DB_PATH = os.getenv("DB_PATH", "/app/data/bot_data.db")

async def init_db():
    global DB_POOL
    if USE_POSTGRES:
        DB_POOL = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)

async def api_get_user_data(request):
    """API endpoint для получения данных пользователя"""
    try:
        user_id = int(request.match_info.get('user_id'))
        
        if USE_POSTGRES:
            async with DB_POOL.acquire() as conn:
                user = await conn.fetchrow("SELECT user_id, first_name FROM users WHERE user_id = $1", user_id)
                if not user:
                    return web.json_response({"error": "User not found"}, status=404)
                
                stats = await conn.fetch("SELECT month, work_days, earnings FROM stats WHERE user_id = $1 ORDER BY saved_at DESC", user_id)
                saved_months = len(stats)
                total_earnings = sum(s['earnings'] for s in stats)
        else:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("SELECT user_id, first_name FROM users WHERE user_id = ?", (user_id,))
                user = await cursor.fetchone()
                if not user:
                    return web.json_response({"error": "User not found"}, status=404)
                
                cursor = await db.execute("SELECT month, work_days, earnings FROM stats WHERE user_id = ? ORDER BY saved_at DESC", (user_id,))
                stats = await cursor.fetchall()
                saved_months = len(stats)
                total_earnings = sum(s[2] for s in stats)
        
        return web.json_response({
            "user_id": user_id,
            "first_name": user[1] if USE_POSTGRES else user[1],
            "saved_months": saved_months,
            "total_earnings": total_earnings
        })
    except Exception as e:
        print(f"API error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def api_send_photo(request):
    """API endpoint для отправки фото в бот"""
    try:
        if not bot:
            return web.json_response({"error": "Bot not configured"}, status=500)
        
        reader = await request.multipart()
        
        user_id = None
        caption = None
        photo_data = None
        
        async for field in reader:
            if field.name == 'user_id':
                user_id = int(await field.text())
            elif field.name == 'caption':
                caption = await field.text()
            elif field.name == 'photo':
                photo_data = await field.read()
        
        if not user_id or not photo_data:
            return web.json_response({"error": "Missing user_id or photo"}, status=400)
        
        # Отправляем фото пользователю
        photo_file = BufferedInputFile(photo_data, filename="stats.png")
        await bot.send_photo(
            chat_id=user_id,
            photo=photo_file,
            caption=caption or "📊 Ваша статистика"
        )
        
        return web.json_response({"success": True, "message": "Photo sent"})
    
    except Exception as e:
        print(f"Send photo error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def main():
    await init_db()
    
    app = web.Application()
    app.router.add_get('/api/user/{user_id}', api_get_user_data)
    app.router.add_post('/api/send_photo', api_send_photo)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()
    
    print("🌐 API сервер запущен на порту 8081")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 API сервер остановлен")
