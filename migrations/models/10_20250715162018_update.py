from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "arrival_to_warehouse" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "arrival_to_warehouse" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "arrival_to_warehouse" ADD "modified_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "arrival_to_warehouse" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        
        ALTER TABLE "delivery_to_recipient" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "delivery_to_recipient" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "delivery_to_recipient" ADD "modified_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "delivery_to_recipient" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        
        ALTER TABLE "issue_to_employee" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "issue_to_employee" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "issue_to_employee" ADD "modified_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "issue_to_employee" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        
        ALTER TABLE "parcels" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "parcels" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "parcels" ADD "modified_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "parcels" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "parcels" DROP COLUMN "recipient_timezone";
        ALTER TABLE "parcels" DROP COLUMN "sender_timezone";
        
        ALTER TABLE "parcel_cargo" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "parcel_cargo" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "parcel_cargo" ADD "modified_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "parcel_cargo" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        
        ALTER TABLE "parcel_products" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "parcel_products" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "parcel_products" ADD "modified_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "parcel_products" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        
        ALTER TABLE "parcel_statuses" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "parcel_statuses" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        
        ALTER TABLE "pickup_from_sender" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "pickup_from_sender" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "pickup_from_sender" ADD "modified_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "pickup_from_sender" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        
        ALTER TABLE "return_to_sender" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "return_to_sender" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "return_to_sender" ADD "modified_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "return_to_sender" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        
        ALTER TABLE "transit" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "transit" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "transit" ADD "modified_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "transit" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        
        ALTER TABLE "transit_details" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "transit_details" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "transit_details" ADD "modified_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
        ALTER TABLE "transit_details" ADD "created_by" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "parcels" ADD "recipient_timezone" VARCHAR(50);
        ALTER TABLE "parcels" ADD "sender_timezone" VARCHAR(50);
        ALTER TABLE "parcels" DROP COLUMN "created_at";
        ALTER TABLE "parcels" DROP COLUMN "modified_at";
        ALTER TABLE "parcels" DROP COLUMN "modified_by";
        ALTER TABLE "parcels" DROP COLUMN "created_by";
        ALTER TABLE "transit" DROP COLUMN "created_at";
        ALTER TABLE "transit" DROP COLUMN "modified_at";
        ALTER TABLE "transit" DROP COLUMN "modified_by";
        ALTER TABLE "transit" DROP COLUMN "created_by";
        ALTER TABLE "parcel_cargo" DROP COLUMN "created_at";
        ALTER TABLE "parcel_cargo" DROP COLUMN "modified_at";
        ALTER TABLE "parcel_cargo" DROP COLUMN "modified_by";
        ALTER TABLE "parcel_cargo" DROP COLUMN "created_by";
        ALTER TABLE "parcel_statuses" DROP COLUMN "created_at";
        ALTER TABLE "parcel_statuses" DROP COLUMN "created_by";
        ALTER TABLE "parcel_products" DROP COLUMN "created_at";
        ALTER TABLE "parcel_products" DROP COLUMN "modified_at";
        ALTER TABLE "parcel_products" DROP COLUMN "modified_by";
        ALTER TABLE "parcel_products" DROP COLUMN "created_by";
        ALTER TABLE "return_to_sender" DROP COLUMN "created_at";
        ALTER TABLE "return_to_sender" DROP COLUMN "modified_at";
        ALTER TABLE "return_to_sender" DROP COLUMN "modified_by";
        ALTER TABLE "return_to_sender" DROP COLUMN "created_by";
        ALTER TABLE "transit_details" DROP COLUMN "created_at";
        ALTER TABLE "transit_details" DROP COLUMN "modified_at";
        ALTER TABLE "transit_details" DROP COLUMN "modified_by";
        ALTER TABLE "transit_details" DROP COLUMN "created_by";
        ALTER TABLE "issue_to_employee" DROP COLUMN "created_at";
        ALTER TABLE "issue_to_employee" DROP COLUMN "modified_at";
        ALTER TABLE "issue_to_employee" DROP COLUMN "modified_by";
        ALTER TABLE "issue_to_employee" DROP COLUMN "created_by";
        ALTER TABLE "pickup_from_sender" DROP COLUMN "created_at";
        ALTER TABLE "pickup_from_sender" DROP COLUMN "modified_at";
        ALTER TABLE "pickup_from_sender" DROP COLUMN "modified_by";
        ALTER TABLE "pickup_from_sender" DROP COLUMN "created_by";
        ALTER TABLE "arrival_to_warehouse" DROP COLUMN "created_at";
        ALTER TABLE "arrival_to_warehouse" DROP COLUMN "modified_at";
        ALTER TABLE "arrival_to_warehouse" DROP COLUMN "modified_by";
        ALTER TABLE "arrival_to_warehouse" DROP COLUMN "created_by";
        ALTER TABLE "delivery_to_recipient" DROP COLUMN "created_at";
        ALTER TABLE "delivery_to_recipient" DROP COLUMN "modified_at";
        ALTER TABLE "delivery_to_recipient" DROP COLUMN "modified_by";
        ALTER TABLE "delivery_to_recipient" DROP COLUMN "created_by";"""
