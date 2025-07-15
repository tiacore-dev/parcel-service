from decimal import Decimal

import pytest

from app.database.models import CargoType, Parcel, ParcelCargo


@pytest.fixture
async def seed_cargo_type(seed_company, seed_user):
    cargo_type = await CargoType.create(
        name="Тестовый груз",
        company_id=seed_company,
        created_by=seed_user,
        modified_by=seed_user,
    )
    return cargo_type


@pytest.fixture
async def seed_parcel_cargo(seed_user, seed_parcel: Parcel, seed_cargo_type):
    cargo = await ParcelCargo.create(
        parcel=seed_parcel,
        weight=Decimal("10.5"),
        length=Decimal("2.5"),
        height=Decimal("1.8"),
        width=Decimal("2.0"),
        volume=Decimal("4.5"),
        quantity=Decimal("2"),
        cargo_type=seed_cargo_type,
        total_weight=Decimal("21.0"),
        total_volume=Decimal("9.0"),
        comment="Тестовый груз",
        created_by=seed_user,
        modified_by=seed_user,
    )
    return cargo
