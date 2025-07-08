from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcel_statuses" ADD "document_type" VARCHAR(50)NOT NULL;
        ALTER TABLE "parcel_statuses" ADD "value_type" VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcel_statuses" DROP COLUMN "document_type";
        ALTER TABLE "parcel_statuses" DROP COLUMN "value_type";"""
