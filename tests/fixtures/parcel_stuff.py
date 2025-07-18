from datetime import datetime
from uuid import uuid4

import pytest

from app.database.models import (
    Arrival,
    ArrivalDetails,
    Delivery,
    Issue,
    IssueDetails,
    Parcel,
    ParcelStatus,
    ParcelStatusEnum,
    Pickup,
    Return,
    ReturnDetails,
    Transit,
    TransitDetails,
    TransitStatusEnum,
)


@pytest.fixture
async def seed_parcel_status(seed_user, seed_parcel: Parcel):
    status = await ParcelStatus.create(
        parcel=seed_parcel,
        document_id=uuid4(),
        document_type="arrival_id",
        status=ParcelStatusEnum.ON_WAREHOUSE,
        value=uuid4(),
        value_type="warehouse_id",
        comment="Тестовый статус",
        created_by=seed_user,
        date=datetime.now(),
    )
    return status


@pytest.fixture
async def seed_pickup_from_sender(seed_user, seed_parcel: Parcel):
    pickup = await Pickup.create(
        warehouse_id=uuid4(),
        employee_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
        sender_name="Иван Иванов",
        created_by=seed_user,
        modified_by=seed_user,
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=pickup.id,
        document_type="pickup_id",
        status=ParcelStatusEnum.ON_WAREHOUSE,
        date=pickup.date,
        value=pickup.warehouse_id,
        value_type="warehouse_id",
        created_by=seed_user,
    )
    return pickup


@pytest.fixture
async def seed_delivery_to_recipient(seed_user, seed_parcel: Parcel):
    delivery = await Delivery.create(
        warehouse_id=uuid4(),
        employee_id=uuid4(),
        date=datetime.now(),
        parcel=seed_parcel,
        recipient_name="Пётр Петров",
        created_by=seed_user,
        modified_by=seed_user,
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=delivery.id,
        document_type="delivery_id",
        status=ParcelStatusEnum.DELIVERED,
        date=delivery.date,
        created_by=seed_user,
    )
    return delivery


@pytest.fixture
async def seed_return(seed_user):
    return_obj = await Return.create(
        warehouse_id=uuid4(),
        employee_id=uuid4(),
        date=datetime.now(),
        sender_name="Иван Иванов",
        created_by=seed_user,
        modified_by=seed_user,
    )
    return return_obj


@pytest.fixture
async def seed_return_details(seed_user, seed_parcel: Parcel, seed_return: Return):
    detail = await ReturnDetails.create(
        parcel=seed_parcel,
        returns=seed_return,
        created_by=seed_user,
        modified_by=seed_user,
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=seed_return.id,
        document_type="return_id",
        status=ParcelStatusEnum.RETURNED,
        date=seed_return.date,
        created_by=seed_user,
    )
    return detail


@pytest.fixture
async def seed_arrival(seed_user):
    arrival = await Arrival.create(
        warehouse_id=uuid4(),
        date=datetime.now(),
        created_by=seed_user,
        modified_by=seed_user,
    )

    return arrival


@pytest.fixture
async def seed_arrival_details(seed_user, seed_parcel: Parcel, seed_arrival: Arrival):
    detail = await ArrivalDetails.create(
        arrival=seed_arrival,
        parcel=seed_parcel,
        created_by=seed_user,
        modified_by=seed_user,
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=seed_arrival.id,
        document_type="arrival_id",
        status=ParcelStatusEnum.ON_WAREHOUSE,
        date=seed_arrival.date,
        value=seed_arrival.warehouse_id,
        value_type="warehouse_id",
        created_by=seed_user,
    )
    return detail


@pytest.fixture
async def seed_issue(seed_user):
    issue = await Issue.create(
        employee_id=uuid4(),
        date=datetime.now(),
        created_by=seed_user,
        modified_by=seed_user,
    )

    return issue


@pytest.fixture
async def seed_issue_details(seed_user, seed_parcel: Parcel, seed_issue: Issue):
    detail = await IssueDetails.create(
        issue=seed_issue,
        parcel=seed_parcel,
        created_by=seed_user,
        modified_by=seed_user,
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=seed_issue.id,
        document_type="issue_id",
        status=ParcelStatusEnum.WITH_EMPLOYEE,
        date=seed_issue.date,
        value=seed_issue.employee_id,
        value_type="user_id",
        created_by=seed_user,
    )
    return detail


@pytest.fixture
async def seed_transit(
    seed_user,
):
    transit = await Transit.create(
        name="0001",
        warehouse_from_id=uuid4(),
        warehouse_to_id=uuid4(),
        date=datetime.now(),
        created_by=seed_user,
        modified_by=seed_user,
        status=TransitStatusEnum.ON_THE_WAY,
    )
    return transit


@pytest.fixture
async def seed_transit_details(seed_user, seed_transit: Transit, seed_parcel: Parcel):
    detail = await TransitDetails.create(
        transit=seed_transit,
        parcel=seed_parcel,
        created_by=seed_user,
        modified_by=seed_user,
    )
    await ParcelStatus.create(
        parcel_id=seed_parcel.id,
        document_id=detail.id,
        document_type="transit_detail_id",
        status=ParcelStatusEnum.IN_TRANSIT,
        date=seed_transit.date,
        created_by=seed_user,
    )
    return detail
