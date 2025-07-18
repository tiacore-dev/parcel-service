import pytest
from httpx import AsyncClient

from app.database.models import Parcel, ReturnDetails


@pytest.mark.asyncio
async def test_add_return_details(test_app: AsyncClient, jwt_token_admin, seed_return, seed_parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "returns_id": str(seed_return.id),
        "parcel_id": str(seed_parcel.id),
    }

    response = await test_app.post("/api/return-details/add", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    detail = await ReturnDetails.get_or_none(id=response_data["details_id"]).prefetch_related("returns", "parcel")

    assert detail is not None
    assert detail.returns.id == seed_return.id
    assert detail.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_return_details(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_return_details,
    seed_return,
    seed_parcel,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "return_id": str(seed_return.id),
        "parcel_id": str(seed_parcel.id),
    }

    response = await test_app.patch(
        f"/api/return-details/{seed_return_details.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    updated = await ReturnDetails.get_or_none(id=seed_return_details.id).prefetch_related("returns", "parcel")
    assert updated is not None
    assert updated.returns.id == seed_return.id
    assert updated.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_view_return_details(test_app: AsyncClient, jwt_token_admin, seed_return_details: ReturnDetails):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/return-details/{seed_return_details.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["details_id"] == str(seed_return_details.id)


@pytest.mark.asyncio
async def test_delete_return_details(test_app: AsyncClient, jwt_token_admin, seed_return_details):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(f"/api/return-details/{seed_return_details.id}", headers=headers)

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await ReturnDetails.get_or_none(id=seed_return_details.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_return_details_list(
    test_app: AsyncClient, jwt_token_admin, seed_return_details: ReturnDetails, seed_parcel: Parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/return-details/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    details = data["details"]

    assert data["total"] >= 1
    assert isinstance(details, list)
    assert any(detail["details_id"] == str(seed_return_details.id) for detail in details)
    assert any(detail["parcel_name"] == seed_parcel.name for detail in details)
