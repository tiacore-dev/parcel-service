from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" ADD "name" VARCHAR(255)NOT NULL UNIQUE;
        ALTER TABLE "pickup_from_sender" ALTER COLUMN "warehouse_id" DROP NOT NULL;
        CREATE UNIQUE INDEX "uid_parcels_name_fa5924" ON "parcels" ("name");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_parcels_name_fa5924";
        ALTER TABLE "parcels" DROP COLUMN "name";
        ALTER TABLE "pickup_from_sender" ALTER COLUMN "warehouse_id" SET NOT NULL;"""
