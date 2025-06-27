from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import PickupFromSender


@pytest.mark.asyncio
async def test_add_pickup_from_sender(
    test_app: AsyncClient, jwt_token_admin, seed_parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "warehouse_id": str(uuid4()),
        "employee_id": str(uuid4()),
        "date": datetime.now().isoformat(),
        "parcel_id": str(seed_parcel.id),
        "sender_name": "Тестовый отправитель",
    }

    response = await test_app.post(
        "/api/pickup-from-sender/add", headers=headers, json=data
    )

    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    pickup = await PickupFromSender.get_or_none(
        id=response_data["pickup_id"]
    ).prefetch_related("parcel")

    assert pickup is not None
    assert pickup.sender_name == "Тестовый отправитель"
    assert pickup.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_pickup_from_sender(
    test_app: AsyncClient, jwt_token_admin, seed_pickup_from_sender: PickupFromSender
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "sender_name": "Обновлённый отправитель",
    }

    response = await test_app.patch(
        f"/api/pickup-from-sender/{seed_pickup_from_sender.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    updated_pickup = await PickupFromSender.get_or_none(id=seed_pickup_from_sender.id)
    assert updated_pickup is not None
    assert updated_pickup.sender_name == "Обновлённый отправитель"


@pytest.mark.asyncio
async def test_view_pickup_from_sender(
    test_app: AsyncClient, jwt_token_admin, seed_pickup_from_sender: PickupFromSender
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        f"/api/pickup-from-sender/{seed_pickup_from_sender.id}", headers=headers
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    assert data["pickup_id"] == str(seed_pickup_from_sender.id)
    assert data["sender_name"] == seed_pickup_from_sender.sender_name


@pytest.mark.asyncio
async def test_delete_pickup_from_sender(
    test_app: AsyncClient, jwt_token_admin, seed_pickup_from_sender: PickupFromSender
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/pickup-from-sender/{seed_pickup_from_sender.id}",
        headers=headers,
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    deleted = await PickupFromSender.get_or_none(id=seed_pickup_from_sender.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_pickup_from_sender_list(
    test_app: AsyncClient, jwt_token_admin, seed_pickup_from_sender: PickupFromSender
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/pickup-from-sender/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    pickups = data["pickups"]

    assert data["total"] >= 1
    assert isinstance(pickups, list)
    assert any(
        pickup["pickup_id"] == str(seed_pickup_from_sender.id) for pickup in pickups
    )
