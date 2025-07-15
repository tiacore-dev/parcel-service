# tests/routes/test_cargo_type.py

import pytest
from httpx import AsyncClient

from app.database.models import CargoType


@pytest.mark.asyncio
async def test_add_cargo_type(test_app: AsyncClient, jwt_token_admin, seed_company):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "cargo_type_name": "Новый груз",
        "company_id": str(seed_company),
    }

    response = await test_app.post("/api/cargo-types/add", headers=headers, json=data)
    assert response.status_code == 201, response.text

    response_data = response.json()
    cargo = await CargoType.get_or_none(id=response_data["cargo_type_id"])
    assert cargo is not None
    assert cargo.name == "Новый груз"
    assert str(cargo.company_id) == str(seed_company)


@pytest.mark.asyncio
async def test_edit_cargo_type(test_app: AsyncClient, jwt_token_admin, seed_cargo_type):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"cargo_type_name": "Обновлённый груз"}

    response = await test_app.patch(f"/api/cargo-types/{seed_cargo_type.id}", headers=headers, json=data)
    assert response.status_code == 200, response.text

    updated = await CargoType.get_or_none(id=seed_cargo_type.id)
    assert updated.name == "Обновлённый груз"  # type: ignore


@pytest.mark.asyncio
async def test_view_cargo_type(test_app: AsyncClient, jwt_token_admin, seed_cargo_type):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get(f"/api/cargo-types/{seed_cargo_type.id}", headers=headers)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["cargo_type_id"] == str(seed_cargo_type.id)
    assert data["cargo_type_name"] == seed_cargo_type.name


@pytest.mark.asyncio
async def test_delete_cargo_type(test_app: AsyncClient, jwt_token_admin, seed_cargo_type):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.delete(f"/api/cargo-types/{seed_cargo_type.id}", headers=headers)
    assert response.status_code == 204

    deleted = await CargoType.get_or_none(id=seed_cargo_type.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_cargo_type_list(test_app: AsyncClient, jwt_token_admin, seed_cargo_type):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/cargo-types/all", headers=headers)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["total"] >= 1
    assert any(t["cargo_type_id"] == str(seed_cargo_type.id) for t in data["types"])
