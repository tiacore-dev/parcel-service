from datetime import datetime
from uuid import uuid4

import pytest

from app.database.models import (
    ArrivalToWarehouse,
    DeliveryToRecipient,
    IssueToEmployee,
    ParcelStatus,
    ParcelStatusEnum,
    PickupFromSender,
    ReturnToSender,
    Transit,
    TransitDetails,
)


@pytest.fixture
async def seed_parcel_status(seed_parcel):
    status = await ParcelStatus.create(
        parcel=seed_parcel,
        document_id=uuid4(),
        status=ParcelStatusEnum.ON_WAREHOUSE,
        value=uuid4(),
        comment="Тестовый статус",
        date=datetime.now(),
    )
    return status


@pytest.fixture
async def seed_pickup_from_sender(seed_parcel):
    pickup = await PickupFromSender.create(
        warehouse_id=uuid4(),
        employee_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
        sender_name="Иван Иванов",
    )
    return pickup


@pytest.fixture
async def seed_delivery_to_recipient(seed_parcel):
    delivery = await DeliveryToRecipient.create(
        warehouse_id=uuid4(),
        employee_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
        recipient_name="Пётр Петров",
    )
    return delivery


@pytest.fixture
async def seed_return_to_sender(seed_parcel):
    return_obj = await ReturnToSender.create(
        warehouse_id=uuid4(),
        employee_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
        sender_name="Иван Иванов",
    )
    return return_obj


@pytest.fixture
async def seed_arrival_to_warehouse(seed_parcel):
    arrival = await ArrivalToWarehouse.create(
        warehouse_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
    )
    return arrival


@pytest.fixture
async def seed_issue_to_employee(seed_parcel):
    issue = await IssueToEmployee.create(
        employee_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
    )
    return issue


@pytest.fixture
async def seed_transit():
    transit = await Transit.create(
        warehouse_from_id=uuid4(),
        warehouse_to_id=uuid4(),
        date=datetime.now(),
    )
    return transit


@pytest.fixture
async def seed_transit_details(seed_transit, seed_parcel):
    detail = await TransitDetails.create(
        transit=seed_transit,
        parcel=seed_parcel,
    )
    return detail
