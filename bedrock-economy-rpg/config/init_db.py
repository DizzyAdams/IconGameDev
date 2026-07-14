import asyncio, os
import asyncpg

async def init_db():
    dsn = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/minecraft")
    schema = open(os.path.join(os.path.dirname(__file__), "schema.sql")).read()
    conn = await asyncpg.connect(dsn)
    await conn.execute(schema)
    await conn.close()
    print("DB schema applied.")

if __name__ == "__main__":
    asyncio.run(init_db())
