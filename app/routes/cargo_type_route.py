from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import CargoType
from app.pydantic_models.cargo_type_models import (
    CargoTypeCreateSchema,
    CargoTypeEditSchema,
    CargoTypeListResponseSchema,
    CargoTypeResponseSchema,
    CargoTypeSchema,
    cargo_type_filter_params,
)

cargo_type_router = APIRouter()

MILLION = 1000000


@cargo_type_router.post(
    "/add",
    response_model=CargoTypeResponseSchema,
    summary="Добавить груз к накладной",
    status_code=status.HTTP_201_CREATED,
)
async def add_cargo_type(
    data: CargoTypeCreateSchema,
    context: dict = Depends(require_permission_in_context("add_cargo_type")),
):
    type = await CargoType.create(created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump())

    return CargoTypeResponseSchema(cargo_type_id=type.id)


@cargo_type_router.patch(
    "/{cargo_type_id}",
    response_model=CargoTypeResponseSchema,
    summary="Редактирование груза накладной",
)
async def edit_cargo_type(
    cargo_type_id: UUID,
    data: CargoTypeEditSchema,
    context: dict = Depends(require_permission_in_context("edit_cargo_type")),
):
    cargo_type = await CargoType.filter(id=cargo_type_id).first()

    if not cargo_type:
        raise HTTPException(status_code=404, detail="Груз не найден")

    update_data = data.model_dump(exclude_unset=True)

    await cargo_type.update_from_dict(update_data)
    cargo_type.modified_by = context["user_id"]
    await cargo_type.save()

    return CargoTypeResponseSchema(cargo_type_id=cargo_type.id)


@cargo_type_router.delete(
    "/{cargo_type_id}",
    summary="Удаление груза накладной",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cargo_type(
    cargo_type_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_cargo_type_type")),
):
    cargo_type = await CargoType.filter(id=cargo_type_id).first()

    if not cargo_type:
        raise HTTPException(status_code=404, detail="Груз не найден")

    await cargo_type.delete()
    return


@cargo_type_router.get(
    "/all",
    response_model=CargoTypeListResponseSchema,
    summary="Получение списка грузов накладных",
)
async def get_cargo_type(
    filters: dict = Depends(cargo_type_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_cargo_types")),
):
    query = Q()

    if filters.get("cargo_type_name"):
        query &= Q(name=filters["cargo_type_name"])

    if filters.get("company_id"):
        query &= Q(company_id=filters["company_id"])

    sort_by = filters.get("sort_by", "created_at")
    if sort_by == "cargo_type_name":
        sort_by = "name"

    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await CargoType.filter(query).count()
    cargo = await CargoType.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return CargoTypeListResponseSchema(
        total=total_count,
        types=[CargoTypeSchema.model_validate(obj, from_attributes=True) for obj in cargo],
    )


@cargo_type_router.get(
    "/{cargo_type_id}",
    response_model=CargoTypeSchema,
    summary="Просмотр одного груза накладной",
)
async def get_cargo_type_by_id(
    cargo_type_id: UUID,
    _: dict = Depends(require_permission_in_context("view_cargo_type")),
):
    cargo_type = await CargoType.filter(id=cargo_type_id).first()

    if not cargo_type:
        raise HTTPException(status_code=404, detail="Груз не найден")

    return CargoTypeSchema.model_validate(cargo_type, from_attributes=True)
