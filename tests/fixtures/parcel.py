from datetime import date, datetime, timedelta
from uuid import uuid4

import pytest

from app.database.models import Parcel


@pytest.fixture
async def seed_parcel():
    now = datetime.now()
    time_from = now.time()
    time_to = (now + timedelta(hours=2)).time()  # например, +2 часа

    parcel = await Parcel.create(
        name="111111",
        sender_city=uuid4(),
        sender_address="ул. Тестовая, д.1",
        sender_company="Тест Отправитель",
        sender_phone="+79999999999",
        pickup_estimated_date=date.today(),
        pickup_time_from=time_from,
        pickup_time_to=time_to,
        sender_additional_info="Тестовая доп. информация",
        recipient_city=uuid4(),
        recipient_address="ул. Получательская, д.2",
        recipient_company="Тест Получатель",
        recipient_phone="+79998887766",
        delivery_estimated_date=date.today(),
        delivery_time_from=time_from,
        delivery_time_to=time_to,
        recipient_additional_info="Доп. инфа по получателю",
        weight=0.0,
        volume=0.0,
        places_count=0,
    )
    return parcel
