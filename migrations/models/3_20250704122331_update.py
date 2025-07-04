from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcel_cargo" ADD "width" DECIMAL(10,2)NOT NULL;
        ALTER TABLE "parcel_cargo" ALTER COLUMN "quantity" TYPE INT USING "quantity"::INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcel_cargo" DROP COLUMN "width";
        ALTER TABLE "parcel_cargo" ALTER COLUMN "quantity" TYPE DECIMAL(10,2) USING "quantity"::DECIMAL(10,2);
        ALTER TABLE "parcel_cargo" ALTER COLUMN "quantity" TYPE DECIMAL(10,2) USING "quantity"::DECIMAL(10,2);"""
