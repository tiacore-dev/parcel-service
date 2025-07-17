from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import Parcel, ReturnToSender


@pytest.mark.asyncio
async def test_add_return_to_sender(test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "warehouse_id": str(uuid4()),
        "employee_id": str(uuid4()),
        "date": datetime.now().isoformat(),
        "parcel_id": str(seed_parcel.id),
        "sender_name": "Тестовый отправитель",
    }

    response = await test_app.post("/api/return/add", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    return_obj = await ReturnToSender.get_or_none(id=response_data["return_id"]).prefetch_related("parcel")

    assert return_obj is not None
    assert return_obj.sender_name == "Тестовый отправитель"
    assert return_obj.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_return_to_sender(test_app: AsyncClient, jwt_token_admin, seed_return_to_sender: ReturnToSender):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "sender_name": "Обновлённый отправитель",
    }

    response = await test_app.patch(
        f"/api/return/{seed_return_to_sender.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    updated_return = await ReturnToSender.get_or_none(id=seed_return_to_sender.id)
    assert updated_return is not None
    assert updated_return.sender_name == "Обновлённый отправитель"


@pytest.mark.asyncio
async def test_view_return_to_sender(test_app: AsyncClient, jwt_token_admin, seed_return_to_sender: ReturnToSender):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/return/{seed_return_to_sender.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["return_id"] == str(seed_return_to_sender.id)
    assert data["sender_name"] == seed_return_to_sender.sender_name


@pytest.mark.asyncio
async def test_delete_return_to_sender(test_app: AsyncClient, jwt_token_admin, seed_return_to_sender: ReturnToSender):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/return/{seed_return_to_sender.id}",
        headers=headers,
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await ReturnToSender.get_or_none(id=seed_return_to_sender.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_return_to_sender_list(
    test_app: AsyncClient, jwt_token_admin, seed_return_to_sender: ReturnToSender, seed_parcel: Parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/return/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    returns = data["returns"]

    assert data["total"] >= 1
    assert isinstance(returns, list)
    assert any(return_["return_id"] == str(seed_return_to_sender.id) for return_ in returns)
    assert any(return_obj["parcel_name"] == seed_parcel.name for return_obj in returns)
