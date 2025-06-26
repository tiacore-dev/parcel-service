from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.database.models import Parcel


@pytest.fixture
async def seed_parcel():
    parcel = await Parcel.create(
        sender_city=uuid4(),
        sender_address="ул. Тестовая, д.1",
        sender_warehouse=uuid4(),
        sender_personal_data=uuid4(),
        sender_company="Тест Отправитель",
        sender_phone="+79999999999",
        sender_email="sender@example.com",
        sender_telegram="@sender",
        sender_coordinates_latitude=Decimal("55.7558"),
        sender_coordinates_longitude=Decimal("37.6176"),
        pickup_estimated_date=date.today(),
        pickup_time_from=datetime.now(),
        pickup_time_to=datetime.now(),
        sender_additional_info="Тестовая доп. информация",
        recipient_city=uuid4(),
        recipient_address="ул. Получательская, д.2",
        recipient_warehouse=uuid4(),
        recipient_personal_data=uuid4(),
        recipient_company="Тест Получатель",
        recipient_phone="+79998887766",
        recipient_email="recipient@example.com",
        recipient_telegram="@recipient",
        recipient_coordinates_latitude=Decimal("59.9343"),
        recipient_coordinates_longitude=Decimal("30.3351"),
        delivery_estimated_date=date.today(),
        delivery_time_from=datetime.now(),
        delivery_time_to=datetime.now(),
        recipient_additional_info="Доп. инфа по получателю",
        note="Примечание",
        weight=Decimal("10.5"),
        volume=Decimal("1.2"),
        places_count=2,
    )
    return parcel
