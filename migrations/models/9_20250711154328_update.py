from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" ALTER COLUMN "volume" TYPE DECIMAL(10,9) USING "volume"::DECIMAL(10,9);
        ALTER TABLE "parcels" ALTER COLUMN "delivery_time_to" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "delivery_estimated_date" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "delivery_time_from" DROP NOT NULL;
        ALTER TABLE "parcel_cargo" ALTER COLUMN "total_volume" TYPE DECIMAL(10,9) USING "total_volume"::DECIMAL(10,9);
        ALTER TABLE "parcel_cargo" ALTER COLUMN "volume" TYPE DECIMAL(10,9) USING "volume"::DECIMAL(10,9);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" ALTER COLUMN "volume" TYPE DECIMAL(10,2) USING "volume"::DECIMAL(10,2);
        ALTER TABLE "parcels" ALTER COLUMN "delivery_time_to" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "delivery_estimated_date" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "delivery_time_from" SET NOT NULL;
        ALTER TABLE "parcel_cargo" ALTER COLUMN "total_volume" TYPE DECIMAL(10,2) USING "total_volume"::DECIMAL(10,2);
        ALTER TABLE "parcel_cargo" ALTER COLUMN "volume" TYPE DECIMAL(10,2) USING "volume"::DECIMAL(10,2);"""
