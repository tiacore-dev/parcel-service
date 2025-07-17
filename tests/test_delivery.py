from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import DeliveryToRecipient, Parcel


@pytest.mark.asyncio
async def test_add_delivery_to_recipient(test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "warehouse_id": str(uuid4()),
        "employee_id": str(uuid4()),
        "date": datetime.now().isoformat(),
        "parcel_id": str(seed_parcel.id),
        "recipient_name": "Тестовый получатель",
    }

    response = await test_app.post("/api/delivery-to-recipient/add", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    delivery = await DeliveryToRecipient.get_or_none(id=response_data["delivery_id"]).prefetch_related("parcel")

    assert delivery is not None
    assert delivery.recipient_name == "Тестовый получатель"
    assert delivery.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_delivery_to_recipient(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_delivery_to_recipient: DeliveryToRecipient,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "recipient_name": "Обновлённый получатель",
    }

    response = await test_app.patch(
        f"/api/delivery-to-recipient/{seed_delivery_to_recipient.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    updated_delivery = await DeliveryToRecipient.get_or_none(id=seed_delivery_to_recipient.id)
    assert updated_delivery is not None
    assert updated_delivery.recipient_name == "Обновлённый получатель"


@pytest.mark.asyncio
async def test_view_delivery_to_recipient(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_delivery_to_recipient: DeliveryToRecipient,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/delivery-to-recipient/{seed_delivery_to_recipient.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["delivery_id"] == str(seed_delivery_to_recipient.id)
    assert data["recipient_name"] == seed_delivery_to_recipient.recipient_name


@pytest.mark.asyncio
async def test_delete_delivery_to_recipient(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_delivery_to_recipient: DeliveryToRecipient,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/delivery-to-recipient/{seed_delivery_to_recipient.id}",
        headers=headers,
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await DeliveryToRecipient.get_or_none(id=seed_delivery_to_recipient.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_delivery_to_recipient_list(
    test_app: AsyncClient, jwt_token_admin, seed_delivery_to_recipient: DeliveryToRecipient, seed_parcel: Parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/delivery-to-recipient/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    deliveries = data["deliveries"]

    assert data["total"] >= 1
    assert isinstance(deliveries, list)
    assert any(delivery["delivery_id"] == str(seed_delivery_to_recipient.id) for delivery in deliveries)
    assert any(delivery["parcel_name"] == seed_parcel.name for delivery in deliveries)
