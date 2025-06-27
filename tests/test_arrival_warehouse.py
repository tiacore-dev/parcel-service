from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import ArrivalToWarehouse


@pytest.mark.asyncio
async def test_add_arrival_to_warehouse(
    test_app: AsyncClient, jwt_token_admin, seed_parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "warehouse_id": str(uuid4()),
        "date": datetime.now().isoformat(),
        "parcel_id": str(seed_parcel.id),
    }

    response = await test_app.post(
        "/api/arrival-to-warehouse/add", headers=headers, json=data
    )

    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    arrival = await ArrivalToWarehouse.get_or_none(
        id=response_data["arrival_id"]
    ).prefetch_related("parcel")

    assert arrival is not None
    assert arrival.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_arrival_to_warehouse(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_arrival_to_warehouse: ArrivalToWarehouse,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "warehouse_id": str(uuid4()),
    }

    response = await test_app.patch(
        f"/api/arrival-to-warehouse/{seed_arrival_to_warehouse.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    updated_arrival = await ArrivalToWarehouse.get_or_none(
        id=seed_arrival_to_warehouse.id
    )
    assert updated_arrival is not None
    assert str(updated_arrival.warehouse_id) == data["warehouse_id"]


@pytest.mark.asyncio
async def test_view_arrival_to_warehouse(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_arrival_to_warehouse: ArrivalToWarehouse,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        f"/api/arrival-to-warehouse/{seed_arrival_to_warehouse.id}", headers=headers
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    assert data["arrival_id"] == str(seed_arrival_to_warehouse.id)


@pytest.mark.asyncio
async def test_delete_arrival_to_warehouse(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_arrival_to_warehouse: ArrivalToWarehouse,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/arrival-to-warehouse/{seed_arrival_to_warehouse.id}",
        headers=headers,
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    deleted = await ArrivalToWarehouse.get_or_none(id=seed_arrival_to_warehouse.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_arrival_to_warehouse_list(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_arrival_to_warehouse: ArrivalToWarehouse,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/arrival-to-warehouse/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    arrivals = data["arrivals"]

    assert data["total"] >= 1
    assert isinstance(arrivals, list)
    assert any(
        arrival["arrival_id"] == str(seed_arrival_to_warehouse.id)
        for arrival in arrivals
    )
