from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transit" ADD "name" VARCHAR(10)NOT NULL UNIQUE;
        CREATE TABLE IF NOT EXISTS "transit_counter" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_number" INT NOT NULL DEFAULT 0
);
        CREATE UNIQUE INDEX "uid_transit_name_cd59e1" ON "transit" ("name");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_transit_name_cd59e1";
        ALTER TABLE "transit" DROP COLUMN "name";
        DROP TABLE IF EXISTS "transit_counter";"""
