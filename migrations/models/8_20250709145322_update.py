from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "parcel_counter" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_number" INT NOT NULL DEFAULT 0
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "parcel_counter";"""
