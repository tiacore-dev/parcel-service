import uuid
from enum import Enum

from tortoise import fields
from tortoise.models import Model


class ParcelStatusEnum(str, Enum):
    ON_WAREHOUSE = "on_warehouse"
    WITH_EMPLOYEE = "with_employee"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"

    def label(self):
        return {
            "on_warehouse": "На складе",
            "with_employee": "У сотрудника",
            "in_transit": "Транзит",
            "delivered": "Доставлено",
            "returned": "Возвращено",
        }[self.value]


class DeliveryType(str, Enum):
    DOOR = "door"
    WAREHOUSE = "warehouse"


class ParcelCounter(Model):
    id = fields.IntField(pk=True)
    last_number = fields.IntField(default=0)

    class Meta:
        table = "parcel_counter"


class Parcel(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255, unique=True)
    company_id = fields.UUIDField()
    # Отправитель
    sender_city = fields.UUIDField()
    sender_timezone = fields.CharField(max_length=50, null=True)
    sender_address = fields.CharField(max_length=255)
    sender_warehouse = fields.UUIDField(null=True)
    sender_delivery_type = fields.CharEnumField(DeliveryType)
    sender_personal_data = fields.UUIDField(null=True)
    sender_company = fields.CharField(max_length=255)
    sender_phone = fields.CharField(max_length=20)
    sender_email = fields.CharField(max_length=100, null=True)
    sender_telegram = fields.CharField(max_length=100, null=True)
    sender_coordinates_latitude = fields.DecimalField(max_digits=9, decimal_places=6, null=True)
    sender_coordinates_longitude = fields.DecimalField(max_digits=9, decimal_places=6, null=True)
    pickup_estimated_date = fields.DateField()
    pickup_time_from = fields.TimeField()
    pickup_time_to = fields.TimeField()
    sender_additional_info = fields.TextField(null=True)

    # Получатель
    recipient_city = fields.UUIDField()
    recipient_timezone = fields.CharField(max_length=50, null=True)
    recipient_address = fields.CharField(max_length=255)
    recipient_warehouse = fields.UUIDField(null=True)
    recipient_delivery_type = fields.CharEnumField(DeliveryType)
    recipient_personal_data = fields.UUIDField(null=True)
    recipient_company = fields.CharField(max_length=255)
    recipient_phone = fields.CharField(max_length=20)
    recipient_email = fields.CharField(max_length=100, null=True)
    recipient_telegram = fields.CharField(max_length=100, null=True)
    recipient_coordinates_latitude = fields.DecimalField(max_digits=9, decimal_places=6, null=True)
    recipient_coordinates_longitude = fields.DecimalField(max_digits=9, decimal_places=6, null=True)
    delivery_estimated_date = fields.DateField(null=True)
    delivery_time_from = fields.TimeField(null=True)
    delivery_time_to = fields.TimeField(null=True)
    recipient_additional_info = fields.TextField(null=True)

    # Общая информация
    note = fields.TextField(null=True)
    weight = fields.DecimalField(max_digits=10, decimal_places=2)
    volume = fields.DecimalField(max_digits=10, decimal_places=9)
    places_count = fields.IntField()

    class Meta:
        table = "parcels"


class ParcelCargo(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    parcel = fields.ForeignKeyField("models.Parcel", related_name="parcel_cargo")
    weight = fields.DecimalField(max_digits=10, decimal_places=2)
    length = fields.DecimalField(max_digits=10, decimal_places=2)
    height = fields.DecimalField(max_digits=10, decimal_places=2)
    width = fields.DecimalField(max_digits=10, decimal_places=2)
    volume = fields.DecimalField(max_digits=10, decimal_places=9)
    quantity = fields.IntField()
    cargo_type = fields.CharField(max_length=100)
    total_weight = fields.DecimalField(max_digits=10, decimal_places=2)
    total_volume = fields.DecimalField(max_digits=10, decimal_places=9)
    comment = fields.TextField(null=True)

    class Meta:
        table = "parcel_cargo"


class ParcelProduct(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    parcel = fields.ForeignKeyField("models.Parcel", related_name="parcel_products")
    name = fields.TextField()
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    quantity = fields.IntField()
    summ = fields.DecimalField(max_digits=10, decimal_places=2)
    article_number = fields.TextField()
    delivered = fields.BooleanField(default=False)
    serial_number = fields.TextField()

    class Meta:
        table = "parcel_products"


class ParcelStatus(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    parcel = fields.ForeignKeyField(
        "models.Parcel",
        related_name="statuses",
        on_delete=fields.CASCADE,
    )
    document_id = fields.UUIDField()
    document_type = fields.CharField(max_length=50)
    status = fields.CharEnumField(ParcelStatusEnum)
    value = fields.UUIDField(null=True)
    value_type = fields.CharField(max_length=255, null=True)
    date = fields.DateField()
    comment = fields.TextField(null=True)

    def to_cache_dict(self):
        return {
            "parcel_id": self.parcel_id,  # type: ignore
            "document_id": self.document_id,
            "document_type": self.document_type,
            "status": self.status,
            "value": self.value,
            "value_type": self.value_type,
            "date": self.date,
            "comment": self.comment,
        }

    class Meta:
        table = "parcel_statuses"


class PickupFromSender(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    warehouse_id = fields.UUIDField(null=True)
    employee_id = fields.UUIDField()
    date = fields.DatetimeField()
    parcel = fields.ForeignKeyField("models.Parcel", related_name="pickup_events")
    sender_name = fields.CharField(max_length=255)

    class Meta:
        table = "pickup_from_sender"


class DeliveryToRecipient(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    warehouse_id = fields.UUIDField()
    employee_id = fields.UUIDField()
    date = fields.DatetimeField()
    parcel = fields.ForeignKeyField("models.Parcel", related_name="delivery_events")
    recipient_name = fields.CharField(max_length=255)

    class Meta:
        table = "delivery_to_recipient"


class ReturnToSender(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    warehouse_id = fields.UUIDField()
    employee_id = fields.UUIDField()
    date = fields.DatetimeField()
    parcel = fields.ForeignKeyField("models.Parcel", related_name="return_events")
    sender_name = fields.CharField(max_length=255)

    class Meta:
        table = "return_to_sender"


class ArrivalToWarehouse(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    warehouse_id = fields.UUIDField()
    date = fields.DatetimeField()
    parcel = fields.ForeignKeyField("models.Parcel", related_name="arrival_events")

    class Meta:
        table = "arrival_to_warehouse"


class IssueToEmployee(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    employee_id = fields.UUIDField()
    date = fields.DatetimeField()
    parcel = fields.ForeignKeyField("models.Parcel", related_name="issue_events")

    class Meta:
        table = "issue_to_employee"


class Transit(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    warehouse_from_id = fields.UUIDField()
    warehouse_to_id = fields.UUIDField()
    date = fields.DatetimeField()

    class Meta:
        table = "transit"


class TransitDetails(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    transit = fields.ForeignKeyField("models.Transit", related_name="details")
    parcel = fields.ForeignKeyField("models.Parcel", related_name="transit_details")

    class Meta:
        table = "transit_details"
