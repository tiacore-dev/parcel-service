from typing import List, Optional, Union
from uuid import UUID

from fastapi import File, Form, Query, UploadFile
from pydantic import BaseModel, Field
from tiacore_lib.utils.validate_helpers import normalize_form_field

from app.database.models import AttachmentEntities


class AttachmentCreateSchema(BaseModel):
    name: str
    description: Optional[str]
    company_id: Optional[UUID]
    entity: AttachmentEntities
    file: UploadFile

    @classmethod
    def as_form(
        cls,
        name: str = Form(..., alias="attachment_name"),
        description: Optional[str] = Form(None),
        company_id: Optional[UUID] = Form(None),
        entity: AttachmentEntities = Form(...),
        file: UploadFile = File(...),
    ):
        return cls(
            name=name,
            description=description,
            company_id=company_id,
            entity=entity,
            file=file,
        )

    class Config:
        from_attributes = True
        populate_by_name = True


class AttachmentEditSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    company_id: Optional[UUID] = None
    entity: Optional[AttachmentEntities] = None
    file: Optional[UploadFile | str] = None

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None, alias="attachment_name"),
        description: Optional[str] = Form(None),
        company_id: Optional[str] = Form(None),  # как строка из формы
        entity: Optional[str] = Form(None),
        file: Optional[Union[str, UploadFile]] = File(None),
    ):
        return cls(
            name=normalize_form_field(name, str),  # type: ignore[arg-type]
            description=normalize_form_field(description, str),  # type: ignore[arg-type]
            company_id=normalize_form_field(company_id, UUID),  # type: ignore[arg-type]
            entity=normalize_form_field(entity, str),  # type: ignore[arg-type]
            file=None if isinstance(file, str) and file.strip() == "" else file,
        )

    class Config:
        from_attributes = True
        populate_by_name = True


class AttachmentResponseSchema(BaseModel):
    attachment_id: UUID

    class Config:
        from_attributes = True
        populate_by_name = True


class AttachmentSchema(BaseModel):
    id: UUID = Field(..., alias="attachment_id")
    name: str = Field(..., alias="attachment_name")
    description: Optional[str] = None
    company_id: Optional[UUID] = None
    entity: AttachmentEntities
    s3_key: str

    class Config:
        from_attributes = True
        populate_by_name = True


class AttachmentListResponseSchema(BaseModel):
    total: int
    attachments: List[AttachmentSchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


def attachment_filter_params(
    company_id: Optional[UUID] = Query(None, description="Фильтр по компании"),
    entity: Optional["str"] = Query(None, description="Фильтр по типу"),
    search: Optional[str] = Query(None, description="Фильтр поиска"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "company_id": company_id,
        "entity": entity,
        "search": search,
        "page": page,
        "page_size": page_size,
    }
