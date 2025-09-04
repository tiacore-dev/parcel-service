from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transits" ALTER COLUMN "name" TYPE VARCHAR(128) USING "name"::VARCHAR(128);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transits" ALTER COLUMN "name" TYPE VARCHAR(10) USING "name"::VARCHAR(10);"""
