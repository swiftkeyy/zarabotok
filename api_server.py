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

async def api_admin_dashboard(request):
    """Admin dashboard data"""
    try:
        if USE_POSTGRES:
            async with DB_POOL.acquire() as conn:
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
                active_today = await conn.fetchval("SELECT COUNT(DISTINCT user_id) FROM stats WHERE saved_at::date = CURRENT_DATE")
                earnings_month = await conn.fetchval("SELECT COALESCE(SUM(earnings), 0) FROM stats WHERE EXTRACT(MONTH FROM saved_at) = EXTRACT(MONTH FROM CURRENT_DATE)")
                goals_count = await conn.fetchval("SELECT COUNT(*) FROM goals WHERE enabled = true")
                
                daily_earnings = await conn.fetch("""
                    SELECT DATE(saved_at) as date, SUM(earnings) as amount
                    FROM stats WHERE saved_at > CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY DATE(saved_at) ORDER BY date
                """)
                
                user_activity = await conn.fetch("""
                    SELECT DATE(last_active) as date, COUNT(*) as count
                    FROM users WHERE last_active > CURRENT_TIMESTAMP - INTERVAL '30 days'
                    GROUP BY DATE(last_active) ORDER BY date
                """)
                
                top_users = await conn.fetch("""
                    SELECT u.first_name as name, COALESCE(SUM(s.earnings), 0) as earnings, COALESCE(SUM(s.work_days), 0) as work_days
                    FROM users u LEFT JOIN stats s ON u.user_id = s.user_id
                    GROUP BY u.user_id, u.first_name ORDER BY earnings DESC LIMIT 10
                """)
        else:
            async with aiosqlite.connect(DB_PATH) as db:
                total_users = (await (await db.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
                active_today = (await (await db.execute("SELECT COUNT(DISTINCT user_id) FROM stats WHERE DATE(saved_at) = DATE('now')")).fetchone())[0]
                earnings_month = (await (await db.execute("SELECT COALESCE(SUM(earnings), 0) FROM stats WHERE strftime('%Y-%m', saved_at) = strftime('%Y-%m', 'now')")).fetchone())[0]
                goals_count = (await (await db.execute("SELECT COUNT(*) FROM goals WHERE enabled = 1")).fetchone())[0]
                
                daily_earnings = await (await db.execute("""
                    SELECT DATE(saved_at) as date, SUM(earnings) as amount
                    FROM stats WHERE saved_at > DATE('now', '-30 days')
                    GROUP BY DATE(saved_at) ORDER BY date
                """)).fetchall()
                
                user_activity = await (await db.execute("""
                    SELECT DATE(last_active) as date, COUNT(*) as count
                    FROM users WHERE last_active > DATETIME('now', '-30 days')
                    GROUP BY DATE(last_active) ORDER BY date
                """)).fetchall()
                
                top_users = await (await db.execute("""
                    SELECT u.first_name as name, COALESCE(SUM(s.earnings), 0) as earnings, COALESCE(SUM(s.work_days), 0) as work_days
                    FROM users u LEFT JOIN stats s ON u.user_id = s.user_id
                    GROUP BY u.user_id ORDER BY earnings DESC LIMIT 10
                """)).fetchall()
        
        return web.json_response({
            "totalUsers": total_users or 0,
            "activeToday": active_today or 0,
            "earningsMonth": earnings_month or 0,
            "goalsCount": goals_count or 0,
            "dailyEarnings": [{"date": str(r[0] if not USE_POSTGRES else r['date']), "amount": r[1] if not USE_POSTGRES else r['amount']} for r in daily_earnings],
            "userActivity": [{"date": str(r[0] if not USE_POSTGRES else r['date']), "count": r[1] if not USE_POSTGRES else r['count']} for r in user_activity],
            "topUsers": [{"name": r[0] if not USE_POSTGRES else r['name'], "earnings": r[1] if not USE_POSTGRES else r['earnings'], "workDays": r[2] if not USE_POSTGRES else r['work_days']} for r in top_users]
        })
    except Exception as e:
        print(f"Dashboard API error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def api_admin_users(request):
    """Get all users with stats"""
    try:
        if USE_POSTGRES:
            async with DB_POOL.acquire() as conn:
                users = await conn.fetch("""
                    SELECT u.user_id, u.first_name, u.username, u.joined_at, u.last_active,
                           COALESCE(SUM(s.earnings), 0) as total_earnings,
                           COUNT(DISTINCT g.id) as goals_count,
                           (u.last_active > CURRENT_TIMESTAMP - INTERVAL '7 days') as is_active
                    FROM users u
                    LEFT JOIN stats s ON u.user_id = s.user_id
                    LEFT JOIN goals g ON u.user_id = g.user_id AND g.enabled = true
                    GROUP BY u.user_id ORDER BY u.joined_at DESC
                """)
        else:
            async with aiosqlite.connect(DB_PATH) as db:
                users = await (await db.execute("""
                    SELECT u.user_id, u.first_name, u.username, u.joined_at, u.last_active,
                           COALESCE(SUM(s.earnings), 0) as total_earnings,
                           COUNT(DISTINCT g.id) as goals_count,
                           (u.last_active > DATETIME('now', '-7 days')) as is_active
                    FROM users u
                    LEFT JOIN stats s ON u.user_id = s.user_id
                    LEFT JOIN goals g ON u.user_id = g.user_id AND g.enabled = 1
                    GROUP BY u.user_id ORDER BY u.joined_at DESC
                """)).fetchall()
        
        users_list = []
        for u in users:
            if USE_POSTGRES:
                users_list.append({
                    "user_id": u['user_id'],
                    "first_name": u['first_name'],
                    "username": u['username'],
                    "joined_at": u['joined_at'].isoformat() if u['joined_at'] else None,
                    "last_active": u['last_active'].isoformat() if u['last_active'] else None,
                    "total_earnings": u['total_earnings'],
                    "goals_count": u['goals_count'],
                    "is_active": u['is_active']
                })
            else:
                users_list.append({
                    "user_id": u[0],
                    "first_name": u[1],
                    "username": u[2],
                    "joined_at": u[3],
                    "last_active": u[4],
                    "total_earnings": u[5],
                    "goals_count": u[6],
                    "is_active": bool(u[7])
                })
        
        return web.json_response({"users": users_list})
    except Exception as e:
        print(f"Users API error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def api_admin_user_detail(request):
    """Get detailed user info"""
    try:
        user_id = int(request.match_info.get('user_id'))
        
        if USE_POSTGRES:
            async with DB_POOL.acquire() as conn:
                user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
                if not user:
                    return web.json_response({"error": "User not found"}, status=404)
                
                total_earnings = await conn.fetchval("SELECT COALESCE(SUM(earnings), 0) FROM stats WHERE user_id = $1", user_id)
                total_work_days = await conn.fetchval("SELECT COALESCE(SUM(work_days), 0) FROM stats WHERE user_id = $1", user_id)
                goals_count = await conn.fetchval("SELECT COUNT(*) FROM goals WHERE user_id = $1 AND enabled = true", user_id)
        else:
            async with aiosqlite.connect(DB_PATH) as db:
                user = await (await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))).fetchone()
                if not user:
                    return web.json_response({"error": "User not found"}, status=404)
                
                total_earnings = (await (await db.execute("SELECT COALESCE(SUM(earnings), 0) FROM stats WHERE user_id = ?", (user_id,))).fetchone())[0]
                total_work_days = (await (await db.execute("SELECT COALESCE(SUM(work_days), 0) FROM stats WHERE user_id = ?", (user_id,))).fetchone())[0]
                goals_count = (await (await db.execute("SELECT COUNT(*) FROM goals WHERE user_id = ? AND enabled = 1", (user_id,))).fetchone())[0]
        
        return web.json_response({
            "user_id": user_id,
            "first_name": user[2] if not USE_POSTGRES else user['first_name'],
            "username": user[1] if not USE_POSTGRES else user['username'],
            "joined_at": user[3] if not USE_POSTGRES else user['joined_at'].isoformat(),
            "total_earnings": total_earnings,
            "total_work_days": total_work_days,
            "goals_count": goals_count
        })
    except Exception as e:
        print(f"User detail API error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def api_admin_goals(request):
    """Get goals and tags stats"""
    try:
        if USE_POSTGRES:
            async with DB_POOL.acquire() as conn:
                goals = await conn.fetch("""
                    SELECT u.first_name as user_name, g.goal_type as type, g.amount, 0 as progress
                    FROM goals g JOIN users u ON g.user_id = u.user_id
                    WHERE g.enabled = true ORDER BY g.amount DESC LIMIT 20
                """)
                
                tags = await conn.fetch("SELECT tag, COUNT(*) as count FROM day_tags GROUP BY tag")
        else:
            async with aiosqlite.connect(DB_PATH) as db:
                goals = await (await db.execute("""
                    SELECT u.first_name as user_name, g.goal_type as type, g.amount, 0 as progress
                    FROM goals g JOIN users u ON g.user_id = u.user_id
                    WHERE g.enabled = 1 ORDER BY g.amount DESC LIMIT 20
                """)).fetchall()
                
                tags = await (await db.execute("SELECT tag, COUNT(*) as count FROM day_tags GROUP BY tag")).fetchall()
        
        goals_list = [{"user_name": g[0] if not USE_POSTGRES else g['user_name'], "type": g[1] if not USE_POSTGRES else g['type'], "amount": g[2] if not USE_POSTGRES else g['amount'], "progress": g[3] if not USE_POSTGRES else g['progress']} for g in goals]
        tags_dict = {t[0] if not USE_POSTGRES else t['tag']: t[1] if not USE_POSTGRES else t['count'] for t in tags}
        
        return web.json_response({"goals": goals_list, "tags": tags_dict})
    except Exception as e:
        print(f"Goals API error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def api_admin_analytics(request):
    """Analytics data"""
    try:
        period = request.query.get('period', 'month')
        
        if USE_POSTGRES:
            async with DB_POOL.acquire() as conn:
                monthly_earnings = await conn.fetch("""
                    SELECT TO_CHAR(saved_at, 'YYYY-MM') as month, SUM(earnings) as amount
                    FROM stats GROUP BY TO_CHAR(saved_at, 'YYYY-MM') ORDER BY month DESC LIMIT 12
                """)
                
                tags_earnings = await conn.fetch("""
                    SELECT dt.tag, COALESCE(SUM(s.earnings), 0) as amount
                    FROM day_tags dt LEFT JOIN stats s ON dt.user_id = s.user_id
                    GROUP BY dt.tag
                """)
        else:
            async with aiosqlite.connect(DB_PATH) as db:
                monthly_earnings = await (await db.execute("""
                    SELECT strftime('%Y-%m', saved_at) as month, SUM(earnings) as amount
                    FROM stats GROUP BY strftime('%Y-%m', saved_at) ORDER BY month DESC LIMIT 12
                """)).fetchall()
                
                tags_earnings = await (await db.execute("""
                    SELECT dt.tag, COALESCE(SUM(s.earnings), 0) as amount
                    FROM day_tags dt LEFT JOIN stats s ON dt.user_id = s.user_id
                    GROUP BY dt.tag
                """)).fetchall()
        
        return web.json_response({
            "monthlyEarnings": [{"month": r[0] if not USE_POSTGRES else r['month'], "amount": r[1] if not USE_POSTGRES else r['amount']} for r in monthly_earnings],
            "tagsEarnings": {r[0] if not USE_POSTGRES else r['tag']: r[1] if not USE_POSTGRES else r['amount'] for r in tags_earnings},
            "retention": []
        })
    except Exception as e:
        print(f"Analytics API error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def api_admin_settings(request):
    """Get/Set admin settings"""
    if request.method == 'GET':
        return web.json_response({
            "welcomeMsg": "Привет! Добро пожаловать в Календарь Заработка!",
            "saveLimit": 10,
            "reminders": "enabled"
        })
    else:
        data = await request.json()
        # Save settings logic here
        return web.json_response({"success": True})

async def api_admin_logs(request):
    """Get admin logs"""
    return web.json_response({"logs": []})

async def main():
    await init_db()
    
    app = web.Application()
    
    # Existing endpoints
    app.router.add_get('/api/user/{user_id}', api_get_user_data)
    app.router.add_post('/api/send_photo', api_send_photo)
    
    # Admin endpoints
    app.router.add_get('/api/admin/dashboard', api_admin_dashboard)
    app.router.add_get('/api/admin/users', api_admin_users)
    app.router.add_get('/api/admin/user/{user_id}', api_admin_user_detail)
    app.router.add_get('/api/admin/goals', api_admin_goals)
    app.router.add_get('/api/admin/analytics', api_admin_analytics)
    app.router.add_route('*', '/api/admin/settings', api_admin_settings)
    app.router.add_get('/api/admin/logs', api_admin_logs)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()
    
    print("🌐 API сервер запущен на порту 8081")
    print("🛠️ Админ API доступен на /api/admin/*")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 API сервер остановлен")
