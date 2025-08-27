from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from tiacore_lib.enums import ServiceType


class GetPriceIDSchema(BaseModel):
    sender_city: UUID = Field(..., alias="sender_city_id")
    recipient_city: UUID = Field(..., alias="recipient_city_id")
    sender_warehouse: Optional[UUID] = Field(None, alias="sender_warehouse_id")
    recipient_warehouse: Optional[UUID] = Field(None, alias="sender_recipient_id")
    service_type: ServiceType

    class Config:
        from_attributes = True
