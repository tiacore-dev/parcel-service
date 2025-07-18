from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "attachments" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "company_id" UUID NOT NULL,
    "description" TEXT,
    "entity" VARCHAR(6) NOT NULL,
    "s3_key" VARCHAR(255) NOT NULL
);
COMMENT ON COLUMN "attachments"."entity" IS 'PARCEL: parcel';
        CREATE TABLE IF NOT EXISTS "templates" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "company_id" UUID NOT NULL,
    "description" TEXT,
    "entity" VARCHAR(6) NOT NULL,
    "s3_key" VARCHAR(255) NOT NULL
);
COMMENT ON COLUMN "templates"."entity" IS 'PARCEL: parcel';
        ALTER TABLE "transits" ALTER COLUMN "status" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transits" ALTER COLUMN "status" SET NOT NULL;
        DROP TABLE IF EXISTS "attachments";
        DROP TABLE IF EXISTS "templates";"""
