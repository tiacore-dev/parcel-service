from typing import List, Optional, Union
from uuid import UUID

from fastapi import File, Form, Query, UploadFile
from pydantic import BaseModel, Field
from tiacore_lib.utils.validate_helpers import normalize_form_field

from app.database.models import TemplateEntities


class GenerateFileSchema(BaseModel):
    template_id: UUID = Form(...)
    entity_id: UUID = Form(...)
    is_pdf: Optional[bool] = Form(False)


class TemplateResponseSchema(BaseModel):
    template_id: UUID

    class Config:
        from_attributes = True
        populate_by_name = True


class TemplateSchema(BaseModel):
    id: UUID = Field(..., alias="template_id")
    name: str = Field(..., alias="template_name")
    description: Optional[str] = None
    company_id: Optional[UUID] = None
    entity: TemplateEntities
    s3_key: str

    class Config:
        from_attributes = True
        populate_by_name = True


class TemplateListResponseSchema(BaseModel):
    total: int
    templates: List[TemplateSchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


def template_filter_params(
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


class TemplateCreateSchema(BaseModel):
    name: str
    description: Optional[str]
    company_id: Optional[UUID]
    entity: TemplateEntities
    file: UploadFile

    @classmethod
    def as_form(
        cls,
        name: str = Form(..., alias="template_name"),
        description: Optional[str] = Form(None),
        company_id: Optional[UUID] = Form(None),
        entity: TemplateEntities = Form(...),
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


class TemplateEditSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    company_id: Optional[UUID] = None
    entity: Optional[TemplateEntities] = None
    file: Optional[UploadFile | str] = None

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None, alias="template_name"),
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
