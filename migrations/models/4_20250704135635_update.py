from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" ADD "recipient_timezone" VARCHAR(50);
        ALTER TABLE "parcels" ADD "sender_timezone" VARCHAR(50);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" DROP COLUMN "recipient_timezone";
        ALTER TABLE "parcels" DROP COLUMN "sender_timezone";"""
