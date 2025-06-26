import pytest
from httpx import AsyncClient

from app.database.models import Parcel, ParcelProduct


@pytest.mark.asyncio
async def test_add_parcel_product(
    test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "parcel_id": str(seed_parcel.id),
        "name": "Тестовый товар",
        "price": "99.99",
        "quantity": 3,
        "article_number": "ART-123",
        "delivered": False,
        "serial_number": "SERIAL-001",
    }

    response = await test_app.post(
        "/api/parcel-products/add", headers=headers, json=data
    )

    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    product = await ParcelProduct.get_or_none(
        id=response_data["product_id"]
    ).prefetch_related("parcel")

    assert product is not None
    assert product.name == "Тестовый товар"
    assert product.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_parcel_product(
    test_app: AsyncClient, jwt_token_admin, seed_parcel_product: ParcelProduct
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "name": "Обновлённый товар",
        "quantity": 5,
    }

    response = await test_app.patch(
        f"/api/parcel-products/{seed_parcel_product.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    updated_product = await ParcelProduct.get_or_none(id=seed_parcel_product.id)
    assert updated_product is not None
    assert updated_product.name == "Обновлённый товар"
    assert updated_product.quantity == 5


@pytest.mark.asyncio
async def test_view_parcel_product(
    test_app: AsyncClient, jwt_token_admin, seed_parcel_product: ParcelProduct
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        f"/api/parcel-products/{seed_parcel_product.id}", headers=headers
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    assert data["product_id"] == str(seed_parcel_product.id)
    assert data["name"] == seed_parcel_product.name


@pytest.mark.asyncio
async def test_delete_parcel_product(
    test_app: AsyncClient, jwt_token_admin, seed_parcel_product: ParcelProduct
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/parcel-products/{seed_parcel_product.id}", headers=headers
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    deleted = await ParcelProduct.get_or_none(id=seed_parcel_product.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_parcel_product_list(
    test_app: AsyncClient, jwt_token_admin, seed_parcel_product: ParcelProduct
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/parcel-products/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    data = response.json()
    products = data["products"]

    assert data["total"] >= 1
    assert isinstance(products, list)
    assert any(
        product["product_id"] == str(seed_parcel_product.id) for product in products
    )


@pytest.mark.parametrize(
    "field,value,expected_type",
    [
        ("quantity", 0, "greater_than_equal"),
        ("quantity", -5, "greater_than_equal"),
        ("price", 0, "greater_than_equal"),
        ("price", -10, "greater_than_equal"),
    ],
)
@pytest.mark.asyncio
async def test_create_parcel_product_validation(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_parcel,
    field,
    value,
    expected_type,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    valid_data = {
        "parcel_id": str(seed_parcel.id),
        "name": "Тестовый товар",
        "price": 10,
        "quantity": 5,
        "article_number": "ART-TEST",
        "delivered": False,
        "serial_number": "SERIAL-TEST",
    }

    invalid_data = {**valid_data, field: value}

    response = await test_app.post(
        "/api/parcel-products/add", headers=headers, json=invalid_data
    )

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(
        error["type"] == expected_type and error["loc"][-1] == field for error in errors
    )
