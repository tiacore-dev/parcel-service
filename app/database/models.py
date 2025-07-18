import uuid
from enum import Enum

from tortoise import fields
from tortoise.fields.relational import ReverseRelation
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


class TransitStatusEnum(str, Enum):
    READY_FOR_LOAD = "ready_for_load"
    READY_FOR_DEPARTURE = "ready_for_departure"
    ON_THE_WAY = "on_the_way"
    UNLOADED_AT_WAREHOUSE = "unloaded_at_warehouse"
    FINISHED = "finished"

    def label(self):
        return {
            "ready_for_load": "Готов к загрузке",
            "ready_for_departure": "Готов к отправке",
            "on_the_way": "В пути",
            "unloaded_at_warehouse": "Выгружен на складе",
            "finished": "Завершен",
        }[self.value]


class DeliveryType(str, Enum):
    DOOR = "door"
    WAREHOUSE = "warehouse"


class ParcelCounter(Model):
    id = fields.IntField(pk=True)
    last_number = fields.IntField(default=0)

    class Meta:
        table = "parcel_counter"


class TransitCounter(Model):
    id = fields.IntField(pk=True)
    last_number = fields.IntField(default=0)

    class Meta:
        table = "transit_counter"


class Parcel(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255, unique=True)
    company_id = fields.UUIDField()
    # Отправитель
    sender_city = fields.UUIDField()
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

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    parcel_cargo: ReverseRelation["ParcelCargo"]
    parcel_products: ReverseRelation["ParcelProduct"]
    statuses: ReverseRelation["ParcelStatus"]

    class Meta:
        table = "parcels"


class CargoType(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=100)
    company_id = fields.UUIDField()

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    parcel_cargo: ReverseRelation["ParcelCargo"]

    class Meta:
        table = "cargo_type"


class ParcelCargo(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    parcel = fields.ForeignKeyField("models.Parcel", related_name="parcel_cargo")
    cargo_type = fields.ForeignKeyField("models.CargoType", related_name="parcel_cargo", null=True)
    weight = fields.DecimalField(max_digits=10, decimal_places=2)
    length = fields.DecimalField(max_digits=10, decimal_places=2)
    height = fields.DecimalField(max_digits=10, decimal_places=2)
    width = fields.DecimalField(max_digits=10, decimal_places=2)
    volume = fields.DecimalField(max_digits=10, decimal_places=9)
    quantity = fields.IntField()
    total_weight = fields.DecimalField(max_digits=10, decimal_places=2)
    total_volume = fields.DecimalField(max_digits=10, decimal_places=9)
    comment = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

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

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

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

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()

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


class Pickup(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    parcel = fields.ForeignKeyField("models.Parcel", related_name="pickup_events")
    warehouse_id = fields.UUIDField(null=True)
    employee_id = fields.UUIDField()
    date = fields.DatetimeField()
    sender_name = fields.CharField(max_length=255)

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "pickups"


class Delivery(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    parcel = fields.ForeignKeyField("models.Parcel", related_name="delivery_events")
    warehouse_id = fields.UUIDField()
    employee_id = fields.UUIDField()
    date = fields.DatetimeField()
    recipient_name = fields.CharField(max_length=255)

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "deliveries"


class Return(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    warehouse_id = fields.UUIDField()
    employee_id = fields.UUIDField()
    date = fields.DatetimeField()
    sender_name = fields.CharField(max_length=255)

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    return_details: ReverseRelation["ReturnDetails"]

    class Meta:
        table = "returns"


class ReturnDetails(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    parcel = fields.ForeignKeyField("models.Parcel", related_name="return_events")
    returns = fields.ForeignKeyField("models.Return", related_name="return_details")

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "return_details"


class Arrival(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    warehouse_id = fields.UUIDField()
    date = fields.DatetimeField()

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    arrival_details: ReverseRelation["ArrivalDetails"]

    class Meta:
        table = "arrivals"


class ArrivalDetails(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    parcel = fields.ForeignKeyField("models.Parcel", related_name="arrival_events")
    arrival = fields.ForeignKeyField("models.Arrival", related_name="arrival_details")

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "arrival_details"


class Issue(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    employee_id = fields.UUIDField()
    date = fields.DatetimeField()

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    issue_details: ReverseRelation["IssueDetails"]

    class Meta:
        table = "issues"


class IssueDetails(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    parcel = fields.ForeignKeyField("models.Parcel", related_name="issue_events")
    issue = fields.ForeignKeyField("models.Issue", related_name="issue_details")

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "issue_details"


class Transit(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=10, unique=True)
    warehouse_from_id = fields.UUIDField()
    warehouse_to_id = fields.UUIDField()
    date = fields.DatetimeField()
    status = fields.CharEnumField(TransitStatusEnum, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    transit_details: ReverseRelation["TransitDetails"]

    class Meta:
        table = "transits"


class TransitDetails(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    transit = fields.ForeignKeyField("models.Transit", related_name="transit_details")
    parcel = fields.ForeignKeyField("models.Parcel", related_name="transit_details")

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "transit_details"


class TemplateEntities(str, Enum):
    PARCEL = "parcel"


class Templates(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    company_id = fields.UUIDField()
    description = fields.TextField(null=True)
    entity = fields.CharEnumField(TemplateEntities)
    s3_key = fields.CharField(max_length=255)

    class Meta:
        table = "templates"


class AttachmentEntities(str, Enum):
    PARCEL = "parcel"


class Attachments(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    company_id = fields.UUIDField()
    description = fields.TextField(null=True)
    entity = fields.CharEnumField(AttachmentEntities)
    entity_id = fields.UUIDField()
    s3_key = fields.CharField(max_length=255)

    class Meta:
        table = "attachments"
