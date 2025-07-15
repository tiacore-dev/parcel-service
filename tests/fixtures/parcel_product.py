from decimal import Decimal

import pytest

from app.database.models import ParcelProduct


@pytest.fixture
async def seed_parcel_product(seed_user, seed_parcel):
    product = await ParcelProduct.create(
        parcel=seed_parcel,
        name="Тестовый товар",
        price=Decimal("99.99"),
        quantity=3,
        summ=Decimal("299.97"),
        article_number="ART-456",
        delivered=False,
        serial_number="SERIAL-456",
        created_by=seed_user,
        modified_by=seed_user,
    )
    return product
