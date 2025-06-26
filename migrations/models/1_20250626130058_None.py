from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "parcels" (
    "id" UUID NOT NULL PRIMARY KEY,
    "sender_city" UUID NOT NULL,
    "sender_address" VARCHAR(255) NOT NULL,
    "sender_warehouse" UUID NOT NULL,
    "sender_personal_data" UUID NOT NULL,
    "sender_company" VARCHAR(255) NOT NULL,
    "sender_phone" VARCHAR(20) NOT NULL,
    "sender_email" VARCHAR(100) NOT NULL,
    "sender_telegram" VARCHAR(100) NOT NULL,
    "sender_coordinates_latitude" DECIMAL(9,6) NOT NULL,
    "sender_coordinates_longitude" DECIMAL(9,6) NOT NULL,
    "pickup_estimated_date" DATE NOT NULL,
    "pickup_time_from" TIMESTAMPTZ NOT NULL,
    "pickup_time_to" TIMESTAMPTZ NOT NULL,
    "sender_additional_info" TEXT,
    "recipient_city" UUID NOT NULL,
    "recipient_address" VARCHAR(255) NOT NULL,
    "recipient_warehouse" UUID NOT NULL,
    "recipient_personal_data" UUID NOT NULL,
    "recipient_company" VARCHAR(255) NOT NULL,
    "recipient_phone" VARCHAR(20) NOT NULL,
    "recipient_email" VARCHAR(100) NOT NULL,
    "recipient_telegram" VARCHAR(100) NOT NULL,
    "recipient_coordinates_latitude" DECIMAL(9,6) NOT NULL,
    "recipient_coordinates_longitude" DECIMAL(9,6) NOT NULL,
    "delivery_estimated_date" DATE NOT NULL,
    "delivery_time_from" TIMESTAMPTZ NOT NULL,
    "delivery_time_to" TIMESTAMPTZ NOT NULL,
    "recipient_additional_info" TEXT,
    "note" TEXT,
    "weight" DECIMAL(10,2) NOT NULL,
    "volume" DECIMAL(10,2) NOT NULL,
    "places_count" INT NOT NULL
);
CREATE TABLE IF NOT EXISTS "arrival_to_warehouse" (
    "id" UUID NOT NULL PRIMARY KEY,
    "warehouse_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "delivery_to_recipient" (
    "id" UUID NOT NULL PRIMARY KEY,
    "warehouse_id" UUID NOT NULL,
    "employee_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "recipient_name" VARCHAR(255) NOT NULL,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "issue_to_employee" (
    "id" UUID NOT NULL PRIMARY KEY,
    "employee_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "parcel_cargo" (
    "id" UUID NOT NULL PRIMARY KEY,
    "weight" DECIMAL(10,2) NOT NULL,
    "length" DECIMAL(10,2) NOT NULL,
    "height" DECIMAL(10,2) NOT NULL,
    "volume" DECIMAL(10,2) NOT NULL,
    "quantity" DECIMAL(10,2) NOT NULL,
    "cargo_type" VARCHAR(100) NOT NULL,
    "total_weight" DECIMAL(10,2) NOT NULL,
    "total_volume" DECIMAL(10,2) NOT NULL,
    "comment" TEXT,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "parcel_products" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "price" DECIMAL(10,2) NOT NULL,
    "quantity" INT NOT NULL,
    "summ" DECIMAL(10,2) NOT NULL,
    "article_number" TEXT NOT NULL,
    "delivered" BOOL NOT NULL DEFAULT False,
    "serial_number" TEXT NOT NULL,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "parcel_statuses" (
    "id" UUID NOT NULL PRIMARY KEY,
    "document_id" UUID NOT NULL,
    "status" VARCHAR(13) NOT NULL,
    "value" UUID NOT NULL,
    "comment" TEXT,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "parcel_statuses"."status" IS 'ON_WAREHOUSE: on_warehouse\nWITH_EMPLOYEE: with_employee\nIN_TRANSIT: in_transit\nDELIVERED: delivered\nRETURNED: returned';
CREATE TABLE IF NOT EXISTS "pickup_from_sender" (
    "id" UUID NOT NULL PRIMARY KEY,
    "warehouse_id" UUID NOT NULL,
    "employee_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "sender_name" VARCHAR(255) NOT NULL,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "return_to_sender" (
    "id" UUID NOT NULL PRIMARY KEY,
    "warehouse_id" UUID NOT NULL,
    "employee_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "sender_name" VARCHAR(255) NOT NULL,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "transit" (
    "id" UUID NOT NULL PRIMARY KEY,
    "warehouse_from_id" UUID NOT NULL,
    "warehouse_to_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS "transit_details" (
    "id" UUID NOT NULL PRIMARY KEY,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE,
    "transit_id" UUID NOT NULL REFERENCES "transit" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
