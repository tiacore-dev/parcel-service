import pytest
from httpx import AsyncClient

from app.database.models import TransitDetails


@pytest.mark.asyncio
async def test_add_transit_details(
    test_app: AsyncClient, jwt_token_admin, seed_transit, seed_parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "transit_id": str(seed_transit.id),
        "parcel_id": str(seed_parcel.id),
    }

    response = await test_app.post(
        "/api/transit-details/add", headers=headers, json=data
    )

    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    detail = await TransitDetails.get_or_none(
        id=response_data["details_id"]
    ).prefetch_related("transit", "parcel")

    assert detail is not None
    assert detail.transit.id == seed_transit.id
    assert detail.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_transit_details(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_transit_details,
    seed_transit,
    seed_parcel,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "transit_id": str(seed_transit.id),
        "parcel_id": str(seed_parcel.id),
    }

    response = await test_app.patch(
        f"/api/transit-details/{seed_transit_details.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    updated = await TransitDetails.get_or_none(
        id=seed_transit_details.id
    ).prefetch_related("transit", "parcel")
    assert updated is not None
    assert updated.transit.id == seed_transit.id
    assert updated.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_view_transit_details(
    test_app: AsyncClient, jwt_token_admin, seed_transit_details
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        f"/api/transit-details/{seed_transit_details.id}", headers=headers
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    assert data["details_id"] == str(seed_transit_details.id)


@pytest.mark.asyncio
async def test_delete_transit_details(
    test_app: AsyncClient, jwt_token_admin, seed_transit_details
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/transit-details/{seed_transit_details.id}", headers=headers
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    deleted = await TransitDetails.get_or_none(id=seed_transit_details.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_transit_details_list(
    test_app: AsyncClient, jwt_token_admin, seed_transit_details
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/transit-details/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    details = data["details"]

    assert data["total"] >= 1
    assert isinstance(details, list)
    assert any(
        detail["details_id"] == str(seed_transit_details.id) for detail in details
    )
