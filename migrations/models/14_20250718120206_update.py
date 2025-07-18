from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "arrivals" (
    "id" UUID NOT NULL PRIMARY KEY,
    "warehouse_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL
);
        CREATE TABLE IF NOT EXISTS "arrival_details" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "arrival_id" UUID NOT NULL REFERENCES "arrivals" ("id") ON DELETE CASCADE,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "deliveries" (
    "id" UUID NOT NULL PRIMARY KEY,
    "warehouse_id" UUID NOT NULL,
    "employee_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "recipient_name" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "issues" (
    "id" UUID NOT NULL PRIMARY KEY,
    "employee_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL
);
        CREATE TABLE IF NOT EXISTS "issue_details" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "issue_id" UUID NOT NULL REFERENCES "issues" ("id") ON DELETE CASCADE,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "pickups" (
    "id" UUID NOT NULL PRIMARY KEY,
    "warehouse_id" UUID,
    "employee_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "sender_name" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "returns" (
    "id" UUID NOT NULL PRIMARY KEY,
    "warehouse_id" UUID NOT NULL,
    "employee_id" UUID NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "sender_name" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL
);
        CREATE TABLE IF NOT EXISTS "return_details" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE,
    "returns_id" UUID NOT NULL REFERENCES "returns" ("id") ON DELETE CASCADE
);
        ALTER TABLE "transit" RENAME TO "transits";
        DROP TABLE IF EXISTS "return_to_sender" CASCADE;
        DROP TABLE IF EXISTS "issue_to_employee" CASCADE;
        DROP TABLE IF EXISTS "pickup_from_sender" CASCADE;
        DROP TABLE IF EXISTS "arrival_to_warehouse" CASCADE;
        DROP TABLE IF EXISTS "delivery_to_recipient" CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transits" RENAME TO "transit";
        DROP TABLE IF EXISTS "arrivals";
        DROP TABLE IF EXISTS "arrival_details";
        DROP TABLE IF EXISTS "deliveries";
        DROP TABLE IF EXISTS "issues";
        DROP TABLE IF EXISTS "issue_details";
        DROP TABLE IF EXISTS "pickups";
        DROP TABLE IF EXISTS "returns";
        DROP TABLE IF EXISTS "return_details";"""
