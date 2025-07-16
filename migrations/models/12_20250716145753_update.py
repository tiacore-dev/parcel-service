from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transit" ADD "status" VARCHAR(21) NOT NULL DEFAULT 'finished';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transit" DROP COLUMN "status";"""
