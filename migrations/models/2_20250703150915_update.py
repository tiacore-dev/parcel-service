from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" ALTER COLUMN "pickup_time_to" TYPE TIMETZ USING "pickup_time_to"::TIMETZ;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_coordinates_longitude" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_email" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_telegram" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "delivery_time_to" TYPE TIMETZ USING "delivery_time_to"::TIMETZ;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_coordinates_latitude" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_warehouse" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "sender_personal_data" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "sender_telegram" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "pickup_time_from" TYPE TIMETZ USING "pickup_time_from"::TIMETZ;
        ALTER TABLE "parcels" ALTER COLUMN "sender_email" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "sender_warehouse" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "sender_coordinates_latitude" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "sender_coordinates_longitude" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_personal_data" DROP NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "delivery_time_from" TYPE TIMETZ USING "delivery_time_from"::TIMETZ;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" ALTER COLUMN "pickup_time_to" TYPE TIMESTAMPTZ USING "pickup_time_to"::TIMESTAMPTZ;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_coordinates_longitude" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_email" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_telegram" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "delivery_time_to" TYPE TIMESTAMPTZ USING "delivery_time_to"::TIMESTAMPTZ;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_coordinates_latitude" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_warehouse" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "sender_personal_data" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "sender_telegram" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "pickup_time_from" TYPE TIMESTAMPTZ USING "pickup_time_from"::TIMESTAMPTZ;
        ALTER TABLE "parcels" ALTER COLUMN "sender_email" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "sender_warehouse" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "sender_coordinates_latitude" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "sender_coordinates_longitude" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "recipient_personal_data" SET NOT NULL;
        ALTER TABLE "parcels" ALTER COLUMN "delivery_time_from" TYPE TIMESTAMPTZ USING "delivery_time_from"::TIMESTAMPTZ;"""
