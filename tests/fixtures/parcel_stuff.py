from datetime import datetime
from uuid import uuid4

import pytest

from app.database.models import (
    ArrivalToWarehouse,
    DeliveryToRecipient,
    IssueToEmployee,
    Parcel,
    ParcelStatus,
    ParcelStatusEnum,
    PickupFromSender,
    ReturnToSender,
    Transit,
    TransitDetails,
)


@pytest.fixture
async def seed_parcel_status(seed_parcel: Parcel):
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
async def seed_pickup_from_sender(seed_parcel: Parcel):
    pickup = await PickupFromSender.create(
        warehouse_id=uuid4(),
        employee_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
        sender_name="Иван Иванов",
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=pickup.id,
        status=ParcelStatusEnum.ON_WAREHOUSE,
        date=pickup.date,
        value=pickup.warehouse_id,
    )
    return pickup


@pytest.fixture
async def seed_delivery_to_recipient(seed_parcel: Parcel):
    delivery = await DeliveryToRecipient.create(
        warehouse_id=uuid4(),
        employee_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
        recipient_name="Пётр Петров",
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=delivery.id,
        status=ParcelStatusEnum.DELIVERED,
        date=delivery.date,
    )
    return delivery


@pytest.fixture
async def seed_return_to_sender(seed_parcel: Parcel):
    return_obj = await ReturnToSender.create(
        warehouse_id=uuid4(),
        employee_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
        sender_name="Иван Иванов",
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=return_obj.id,
        status=ParcelStatusEnum.RETURNED,
        date=return_obj.date,
    )
    return return_obj


@pytest.fixture
async def seed_arrival_to_warehouse(seed_parcel: Parcel):
    arrival = await ArrivalToWarehouse.create(
        warehouse_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=arrival.id,
        status=ParcelStatusEnum.ON_WAREHOUSE,
        date=arrival.date,
        value=arrival.warehouse_id,
    )
    return arrival


@pytest.fixture
async def seed_issue_to_employee(seed_parcel: Parcel):
    issue = await IssueToEmployee.create(
        employee_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=issue.id,
        status=ParcelStatusEnum.WITH_EMPLOYEE,
        date=issue.date,
        value=issue.employee_id,
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
async def seed_transit_details(seed_transit: Transit, seed_parcel: Parcel):
    detail = await TransitDetails.create(
        transit=seed_transit,
        parcel=seed_parcel,
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=detail.id,
        status=ParcelStatusEnum.IN_TRANSIT,
        date=seed_transit.date,
    )
    return detail
