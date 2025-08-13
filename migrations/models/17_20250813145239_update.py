from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "attachmententityrelation" (
    "id" UUID NOT NULL PRIMARY KEY
);
        ALTER TABLE "parcel_statuses" ALTER COLUMN "date" TYPE TIMESTAMPTZ USING "date"::TIMESTAMPTZ;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcel_statuses" ALTER COLUMN "date" TYPE DATE USING "date"::DATE;
        DROP TABLE IF EXISTS "attachmententityrelation";"""
