import pytest
from httpx import AsyncClient

from app.database.models import Parcel, ParcelCargo


@pytest.mark.asyncio
async def test_add_parcel_cargo(
    test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "parcel_id": str(seed_parcel.id),
        "weight": "10.5",
        "length": "2.5",
        "height": "1.8",
        "quantity": "2",
        "cargo_type": "Коробка",
        "comment": "Комментарий к грузу",
    }

    response = await test_app.post("/api/parcel-cargo/add", headers=headers, json=data)

    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    cargo = await ParcelCargo.get_or_none(
        id=response_data["cargo_id"]
    ).prefetch_related("parcel")

    assert cargo is not None
    assert cargo.cargo_type == "Коробка"
    assert cargo.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_parcel_cargo(
    test_app: AsyncClient, jwt_token_admin, seed_parcel_cargo: ParcelCargo
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "cargo_type": "Обновлённый тип",
        "comment": "Обновлённый комментарий",
    }

    response = await test_app.patch(
        f"/api/parcel-cargo/{seed_parcel_cargo.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    updated_cargo = await ParcelCargo.get_or_none(
        id=seed_parcel_cargo.id
    ).prefetch_related("parcel")
    assert updated_cargo is not None
    assert updated_cargo.cargo_type == "Обновлённый тип"
    assert updated_cargo.comment == "Обновлённый комментарий"


@pytest.mark.asyncio
async def test_view_parcel_cargo(
    test_app: AsyncClient, jwt_token_admin, seed_parcel_cargo: ParcelCargo
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        f"/api/parcel-cargo/{seed_parcel_cargo.id}", headers=headers
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    assert data["cargo_id"] == str(seed_parcel_cargo.id)
    assert data["cargo_type"] == seed_parcel_cargo.cargo_type


@pytest.mark.asyncio
async def test_delete_parcel_cargo(
    test_app: AsyncClient, jwt_token_admin, seed_parcel_cargo: ParcelCargo
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/parcel-cargo/{seed_parcel_cargo.id}", headers=headers
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    deleted = await ParcelCargo.get_or_none(id=seed_parcel_cargo.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_parcel_cargo_list(
    test_app: AsyncClient, jwt_token_admin, seed_parcel_cargo: ParcelCargo
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/parcel-cargo/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    cargo_list = data["cargo"]

    assert data["total"] >= 1
    assert isinstance(cargo_list, list)
    assert any(cargo["cargo_id"] == str(seed_parcel_cargo.id) for cargo in cargo_list)
