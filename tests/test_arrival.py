from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import Arrival, ArrivalDetails, Parcel, ParcelStatusEnum
from app.handlers.status_handler import get_cached_parcel_status_data


@pytest.mark.asyncio
async def test_add_arrival(test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "warehouse_id": str(uuid4()),
        "date": datetime.now().isoformat(),
    }

    response = await test_app.post("/api/arrivals/add", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    arrival = await Arrival.get_or_none(id=response_data["arrival_id"])

    assert arrival is not None


@pytest.mark.asyncio
async def test_add_arrival_bulk(test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {"warehouse_id": str(uuid4()), "date": datetime.now().isoformat(), "parcels": [str(seed_parcel.id)]}

    response = await test_app.post("/api/arrivals/add-bulk", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    arrival = await Arrival.get_or_none(id=response_data["arrival_id"])

    detail = await ArrivalDetails.get_or_none(parcel_id=seed_parcel.id)
    assert arrival is not None
    assert detail is not None
    status = await get_cached_parcel_status_data(seed_parcel.id)
    assert status is not None
    assert status["status"] == ParcelStatusEnum.ON_WAREHOUSE


@pytest.mark.asyncio
async def test_edit_arrival(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_arrival: Arrival,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "warehouse_id": str(uuid4()),
    }

    response = await test_app.patch(
        f"/api/arrivals/{seed_arrival.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    updated_arrival = await Arrival.get_or_none(id=seed_arrival.id)
    assert updated_arrival is not None
    assert str(updated_arrival.warehouse_id) == data["warehouse_id"]


@pytest.mark.asyncio
async def test_view_arrival(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_arrival: Arrival,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/arrivals/{seed_arrival.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["arrival_id"] == str(seed_arrival.id)


@pytest.mark.asyncio
async def test_delete_arrival(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_arrival: Arrival,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/arrivals/{seed_arrival.id}",
        headers=headers,
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await Arrival.get_or_none(id=seed_arrival.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_arrival_list(test_app: AsyncClient, jwt_token_admin, seed_arrival: Arrival, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    query_params = {"parcel_name": seed_parcel.name}
    response = await test_app.get("/api/arrivals/all", headers=headers, params=query_params)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    arrivals = data["arrivals"]

    assert data["total"] >= 1
    assert isinstance(arrivals, list)
    assert any(arrival["arrival_id"] == str(seed_arrival.id) for arrival in arrivals)
