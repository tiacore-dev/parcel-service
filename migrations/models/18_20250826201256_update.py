from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "services" (
    "id" UUID NOT NULL PRIMARY KEY,
    "contract_id" UUID NOT NULL,
    "price_id" UUID,
    "service_type" VARCHAR(8) NOT NULL,
    "base_value" DOUBLE PRECISION NOT NULL,
    "summ" DOUBLE PRECISION,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "parcel_id" UUID NOT NULL REFERENCES "parcels" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "services"."service_type" IS 'STANDARD: standard\nEXPRESS: express\nTHERMAL: thermal\nFRAGILE: fragile\nPERSONAL: personal';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "services";"""
