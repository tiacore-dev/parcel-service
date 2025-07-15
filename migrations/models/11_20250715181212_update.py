from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "cargo_type" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "company_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL
);
        ALTER TABLE "parcel_cargo" ADD "cargo_type_id" UUID;
        ALTER TABLE "parcel_cargo" DROP COLUMN "cargo_type";
        ALTER TABLE "parcel_cargo" ADD CONSTRAINT "fk_parcel_c_cargo_ty_6ef2149b" FOREIGN KEY ("cargo_type_id") REFERENCES "cargo_type" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcel_cargo" DROP CONSTRAINT "fk_parcel_c_cargo_ty_6ef2149b";
        ALTER TABLE "parcel_cargo" ADD "cargo_type" VARCHAR(100)NOT NULL;
        ALTER TABLE "parcel_cargo" DROP COLUMN "cargo_type_id";
        DROP TABLE IF EXISTS "cargo_type";"""
