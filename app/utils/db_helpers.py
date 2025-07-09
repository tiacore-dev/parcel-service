from tortoise import Tortoise
from tortoise.transactions import in_transaction

from app.database.models import ParcelCounter


async def drop_all_tables():
    conn = Tortoise.get_connection("default")
    tables = await conn.execute_query_dict("""
        SELECT tablename FROM pg_tables WHERE schemaname = 'public';
    """)
    async with in_transaction() as tx:
        for table in tables:
            await tx.execute_query(f'DROP TABLE IF EXISTS "{table["tablename"]}" CASCADE;')


async def generate_parcel_name() -> str:
    async with in_transaction():
        counter, _ = await ParcelCounter.get_or_create(id=1)
        counter.last_number += 1
        await counter.save()
        return f"{counter.last_number:09d}"  # Формат: 000000001
