import pytest
from httpx import AsyncClient

from app.database.models import ParcelStatus


@pytest.mark.asyncio
async def test_view_parcel_status(
    test_app: AsyncClient, jwt_token_admin, seed_parcel_status: ParcelStatus
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        f"/api/parcel-status/{seed_parcel_status.id}", headers=headers
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    assert data["status_id"] == str(seed_parcel_status.id)
    assert data["status"] == seed_parcel_status.status


@pytest.mark.asyncio
async def test_get_parcel_status_list(
    test_app: AsyncClient, jwt_token_admin, seed_parcel_status: ParcelStatus
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/parcel-status/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    statuses = data["statuses"]

    assert data["total"] >= 1
    assert isinstance(statuses, list)
    assert any(status["status_id"] == str(seed_parcel_status.id) for status in statuses)
