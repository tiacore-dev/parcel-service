from fastapi import APIRouter

from app.database.models import ParcelStatusEnum

status_router = APIRouter()


@status_router.get("/statuses")
def get_statuses():
    return [
        {"value": status.value, "label": status.label()} for status in ParcelStatusEnum
    ]
