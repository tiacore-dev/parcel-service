from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import Transit


@pytest.mark.asyncio
async def test_add_transit(test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "warehouse_from_id": str(uuid4()),
        "warehouse_to_id": str(uuid4()),
        "date": datetime.now().isoformat(),
        "status": "on_the_way",
    }

    response = await test_app.post("/api/transit/add", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    transit = await Transit.get_or_none(id=response_data["transit_id"])

    assert transit is not None
    assert str(transit.warehouse_from_id) == data["warehouse_from_id"]
    assert str(transit.warehouse_to_id) == data["warehouse_to_id"]


@pytest.mark.asyncio
async def test_edit_transit(test_app: AsyncClient, jwt_token_admin, seed_transit: Transit):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    new_warehouse_to_id = uuid4()

    data = {"warehouse_to_id": str(new_warehouse_to_id), "status": "finished"}

    response = await test_app.patch(
        f"/api/transit/{seed_transit.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    updated_transit = await Transit.get_or_none(id=seed_transit.id)
    assert updated_transit is not None
    assert str(updated_transit.warehouse_to_id) == str(new_warehouse_to_id)
    assert updated_transit.status == "finished"


@pytest.mark.asyncio
async def test_view_transit(test_app: AsyncClient, jwt_token_admin, seed_transit: Transit):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/transit/{seed_transit.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["transit_id"] == str(seed_transit.id)


@pytest.mark.asyncio
async def test_delete_transit(test_app: AsyncClient, jwt_token_admin, seed_transit: Transit):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(f"/api/transit/{seed_transit.id}", headers=headers)

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await Transit.get_or_none(id=seed_transit.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_transit_list(test_app: AsyncClient, jwt_token_admin, seed_transit: Transit):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/transit/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    transits = data["transits"]

    assert data["total"] >= 1
    assert isinstance(transits, list)
    assert any(transit["transit_id"] == str(seed_transit.id) for transit in transits)
