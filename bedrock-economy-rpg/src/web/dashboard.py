from fastapi import FastAPI, HTTPException
from typing import Optional
import asyncpg, os

app = FastAPI(title="Bedrock Minemods API")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://mcuser:mcpass@localhost:5432/minecraft")


async def get_pool():
    return await asyncpg.create_pool(DATABASE_URL)


@app.on_event("startup")
async def startup():
    app.state.pool = await get_pool()


@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()


@app.get("/api/player/{xuid}")
async def get_player(xuid: str):
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM players WHERE xuid = $1", xuid)
        if not row:
            raise HTTPException(404, "Player not found")
        return dict(row)


@app.get("/api/economy/top")
async def top_balance(limit: int = 10):
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT name, coins, level FROM players ORDER BY coins DESC LIMIT $1", limit)
        return [dict(r) for r in rows]


@app.get("/api/economy/stats")
async def economy_stats():
    async with app.state.pool.acquire() as conn:
        total = await conn.fetchval("SELECT SUM(coins) FROM players")
        count = await conn.fetchval("SELECT COUNT(*) FROM players")
        top = await conn.fetchval("SELECT MAX(coins) FROM players")
        tx_24h = await conn.fetchval(
            "SELECT COUNT(*) FROM economy_transactions WHERE created_at > NOW() - INTERVAL '24 hours'"
        )
        return {"total_coins": total or 0, "total_players": count or 0, "top_balance": top or 0, "transactions_24h": tx_24h or 0}


@app.get("/api/rpg/top")
async def top_level(limit: int = 10):
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT name, level, xp, class FROM players ORDER BY level DESC, xp DESC LIMIT $1", limit)
        return [dict(r) for r in rows]


@app.get("/api/server/status")
async def server_status():
    async with app.state.pool.acquire() as conn:
        await conn.fetchval("SELECT 1")
        return {"status": "online", "database": "connected"}
