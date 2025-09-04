import pytest
from httpx import AsyncClient

from app.database.models import Service

# @pytest.mark.asyncio
# async def test_add_service(test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel):
#     headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

#     data = {
#         "service_type": "standard",
#         "parcel_id": str(seed_parcel.id),
#         "contract_id": str(uuid4()),
#         "price_id": str(uuid4()),
#         "base_value": 1,
#     }

#     response = await test_app.post("/api/services/add", headers=headers, json=data)

#     assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

#     response_data = response.json()
#     service = await Service.get_or_none(id=response_data["service_id"])

#     assert service is not None


# @pytest.mark.asyncio
# async def test_edit_service(test_app: AsyncClient, jwt_token_admin, seed_service: Service):
#     headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

#     data = {
#         "contract_id": str(uuid4()),
#     }

#     response = await test_app.patch(
#         f"/api/services/{seed_service.id}",
#         headers=headers,
#         json=data,
#     )

#     assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

#     updated_service = await Service.get_or_none(id=seed_service.id)
#     assert updated_service is not None
#     assert str(updated_service.contract_id) == data["contract_id"]


@pytest.mark.asyncio
async def test_view_service(test_app: AsyncClient, jwt_token_admin, seed_service: Service):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/services/{seed_service.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["service_id"] == str(seed_service.id)


@pytest.mark.asyncio
async def test_delete_service(test_app: AsyncClient, jwt_token_admin, seed_service: Service):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/services/{seed_service.id}",
        headers=headers,
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await Service.get_or_none(id=seed_service.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_service_list(test_app: AsyncClient, jwt_token_admin, seed_service: Service):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/services/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    services = data["services"]

    assert data["total"] >= 1
    assert isinstance(services, list)
    assert any(service["service_id"] == str(seed_service.id) for service in services)
