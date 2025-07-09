from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" ADD "recipient_delivery_type" VARCHAR(9) NOT NULL DEFAULT 'door';
        ALTER TABLE "parcels" ADD "sender_delivery_type" VARCHAR(9) NOT NULL DEFAULT 'door';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" DROP COLUMN "recipient_delivery_type";
        ALTER TABLE "parcels" DROP COLUMN "sender_delivery_type";"""
