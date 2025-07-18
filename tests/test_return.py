from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import Parcel, Return, ReturnDetails


@pytest.mark.asyncio
async def test_add_return(test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "warehouse_id": str(uuid4()),
        "employee_id": str(uuid4()),
        "date": datetime.now().isoformat(),
        "sender_name": "Тестовый отправитель",
    }

    response = await test_app.post("/api/returns/add", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    return_obj = await Return.get_or_none(id=response_data["return_id"])

    assert return_obj is not None
    assert return_obj.sender_name == "Тестовый отправитель"


@pytest.mark.asyncio
async def test_add_return_bulk(test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "warehouse_id": str(uuid4()),
        "employee_id": str(uuid4()),
        "date": datetime.now().isoformat(),
        "sender_name": "Тестовый отправитель",
        "parcels": [str(seed_parcel.id)],
    }

    response = await test_app.post("/api/returns/add-bulk", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    return_obj = await Return.get_or_none(id=response_data["return_id"])

    detail = await ReturnDetails.get_or_none(parcel_id=seed_parcel.id)
    assert return_obj is not None
    assert detail is not None


@pytest.mark.asyncio
async def test_edit_return(test_app: AsyncClient, jwt_token_admin, seed_return: Return):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "sender_name": "Обновлённый отправитель",
    }

    response = await test_app.patch(
        f"/api/returns/{seed_return.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    updated_return = await Return.get_or_none(id=seed_return.id)
    assert updated_return is not None
    assert updated_return.sender_name == "Обновлённый отправитель"


@pytest.mark.asyncio
async def test_view_return(test_app: AsyncClient, jwt_token_admin, seed_return: Return):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/returns/{seed_return.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["return_id"] == str(seed_return.id)
    assert data["sender_name"] == seed_return.sender_name


@pytest.mark.asyncio
async def test_delete_return(test_app: AsyncClient, jwt_token_admin, seed_return: Return):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/returns/{seed_return.id}",
        headers=headers,
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await Return.get_or_none(id=seed_return.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_return_list(test_app: AsyncClient, jwt_token_admin, seed_return: Return, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/returns/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    returns = data["returns"]

    assert data["total"] >= 1
    assert isinstance(returns, list)
    assert any(return_["return_id"] == str(seed_return.id) for return_ in returns)
