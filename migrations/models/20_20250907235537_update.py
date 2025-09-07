from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" ALTER COLUMN "weight" TYPE DECIMAL(12,3) USING "weight"::DECIMAL(12,3);
        ALTER TABLE "parcels" ALTER COLUMN "volume" TYPE DECIMAL(14,6) USING "volume"::DECIMAL(14,6);
        ALTER TABLE "parcel_cargo" ALTER COLUMN "total_volume" TYPE DECIMAL(14,6) USING "total_volume"::DECIMAL(14,6);
        ALTER TABLE "parcel_cargo" ALTER COLUMN "volume" TYPE DECIMAL(14,6) USING "volume"::DECIMAL(14,6);
        ALTER TABLE "parcel_cargo" ALTER COLUMN "total_weight" TYPE DECIMAL(12,3) USING "total_weight"::DECIMAL(12,3);
        ALTER TABLE "services" ALTER COLUMN "summ" TYPE DECIMAL(12,2) USING "summ"::DECIMAL(12,2);
        ALTER TABLE "services" ALTER COLUMN "summ" TYPE DECIMAL(12,2) USING "summ"::DECIMAL(12,2);
        ALTER TABLE "services" ALTER COLUMN "base_value" TYPE DECIMAL(10,3) USING "base_value"::DECIMAL(10,3);
        ALTER TABLE "services" ALTER COLUMN "base_value" TYPE DECIMAL(10,3) USING "base_value"::DECIMAL(10,3);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" ALTER COLUMN "weight" TYPE DECIMAL(10,2) USING "weight"::DECIMAL(10,2);
        ALTER TABLE "parcels" ALTER COLUMN "volume" TYPE DECIMAL(10,9) USING "volume"::DECIMAL(10,9);
        ALTER TABLE "services" ALTER COLUMN "summ" TYPE DOUBLE PRECISION USING "summ"::DOUBLE PRECISION;
        ALTER TABLE "services" ALTER COLUMN "base_value" TYPE DOUBLE PRECISION USING "base_value"::DOUBLE PRECISION;
        ALTER TABLE "parcel_cargo" ALTER COLUMN "total_volume" TYPE DECIMAL(10,9) USING "total_volume"::DECIMAL(10,9);
        ALTER TABLE "parcel_cargo" ALTER COLUMN "volume" TYPE DECIMAL(10,9) USING "volume"::DECIMAL(10,9);
        ALTER TABLE "parcel_cargo" ALTER COLUMN "total_weight" TYPE DECIMAL(10,2) USING "total_weight"::DECIMAL(10,2);"""
