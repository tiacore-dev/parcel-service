from fastapi import APIRouter

from app.database.models import ParcelStatusEnum, TransitStatusEnum

status_router = APIRouter()


@status_router.get("/parcel-statuses")
def get_parcel_statuses():
    return [{"value": status.value, "label": status.label()} for status in ParcelStatusEnum]


@status_router.get("/transit-statuses")
def get_transit_statuses():
    return [{"value": status.value, "label": status.label()} for status in TransitStatusEnum]
