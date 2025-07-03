from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import Parcel


@pytest.mark.asyncio
async def test_add_parcel(test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "parcel_name": "1111",
        "sender_city": str(uuid4()),
        "sender_address": "ул. Тестовая, д.1",
        "sender_company": "Тест Отправитель",
        "sender_phone": "+79999999999",
        "pickup_estimated_date": "2025-06-25",
        "pickup_time_from": "10:00:00",
        "pickup_time_to": "12:00:00",
        "recipient_city": str(uuid4()),
        "recipient_address": "ул. Получательская, д.2",
        "recipient_company": "Тест Получатель",
        "recipient_phone": "+79998887766",
        "delivery_estimated_date": "2025-06-26",
        "delivery_time_from": "10:00:00",
        "delivery_time_to": "12:00:00",
        "recipient_additional_info": "Доп. инфа по получателю",
    }

    response = await test_app.post("/api/parcels/add", headers=headers, json=data)

    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    parcel = await Parcel.get_or_none(id=response_data["parcel_id"])

    assert parcel is not None
    assert parcel.sender_company == "Тест Отправитель"
    assert parcel.recipient_company == "Тест Получатель"


@pytest.mark.asyncio
async def test_edit_parcel(test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "note": "Обновленное примечание",
        "places_count": 5,
    }

    response = await test_app.patch(
        f"/api/parcels/{seed_parcel.id}", headers=headers, json=data
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    updated_parcel = await Parcel.get_or_none(id=seed_parcel.id)
    assert updated_parcel is not None
    assert updated_parcel.note == "Обновленное примечание"
    assert updated_parcel.places_count == 5


@pytest.mark.asyncio
async def test_view_parcel(test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/parcels/{seed_parcel.id}", headers=headers)
    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    assert data["parcel_id"] == str(seed_parcel.id)
    assert data["sender_company"] == seed_parcel.sender_company
    assert data["recipient_company"] == seed_parcel.recipient_company


@pytest.mark.asyncio
async def test_delete_parcel(
    test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(f"/api/parcels/{seed_parcel.id}", headers=headers)
    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    deleted = await Parcel.get_or_none(id=seed_parcel.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_parcels(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_parcel: Parcel,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/parcels/all", headers=headers)
    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    parcels = data["parcels"]

    assert data["total"] >= 1
    assert isinstance(parcels, list)
    assert any(parcel["parcel_id"] == str(seed_parcel.id) for parcel in parcels)
