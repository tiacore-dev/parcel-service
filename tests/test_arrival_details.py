import pytest
from httpx import AsyncClient

from app.database.models import ArrivalDetails, Parcel


@pytest.mark.asyncio
async def test_add_arrival_details(test_app: AsyncClient, jwt_token_admin, seed_arrival, seed_parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "arrival_id": str(seed_arrival.id),
        "parcel_id": str(seed_parcel.id),
    }

    response = await test_app.post("/api/arrival-details/add", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    detail = await ArrivalDetails.get_or_none(id=response_data["details_id"]).prefetch_related("arrival", "parcel")

    assert detail is not None
    assert detail.arrival.id == seed_arrival.id
    assert detail.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_arrival_details(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_arrival_details,
    seed_arrival,
    seed_parcel,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "arrival_id": str(seed_arrival.id),
        "parcel_id": str(seed_parcel.id),
    }

    response = await test_app.patch(
        f"/api/arrival-details/{seed_arrival_details.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    updated = await ArrivalDetails.get_or_none(id=seed_arrival_details.id).prefetch_related("arrival", "parcel")
    assert updated is not None
    assert updated.arrival.id == seed_arrival.id
    assert updated.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_view_arrival_details(test_app: AsyncClient, jwt_token_admin, seed_arrival_details: ArrivalDetails):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/arrival-details/{seed_arrival_details.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["details_id"] == str(seed_arrival_details.id)


@pytest.mark.asyncio
async def test_delete_arrival_details(test_app: AsyncClient, jwt_token_admin, seed_arrival_details):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(f"/api/arrival-details/{seed_arrival_details.id}", headers=headers)

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await ArrivalDetails.get_or_none(id=seed_arrival_details.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_arrival_details_list(
    test_app: AsyncClient, jwt_token_admin, seed_arrival_details: ArrivalDetails, seed_parcel: Parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/arrival-details/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    details = data["details"]

    assert data["total"] >= 1
    assert isinstance(details, list)
    assert any(detail["details_id"] == str(seed_arrival_details.id) for detail in details)
    assert any(detail["parcel_name"] == seed_parcel.name for detail in details)
