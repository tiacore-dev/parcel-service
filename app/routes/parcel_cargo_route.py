from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Parcel, ParcelCargo
from app.pydantic_models.parcel_cargo_models import (
    ParcelCargoCreateSchema,
    ParcelCargoEditSchema,
    ParcelCargoListResponseSchema,
    ParcelCargoResponseSchema,
    ParcelCargoSchema,
    parcel_cargo_filter_params,
)

parcel_cargo_router = APIRouter()


@parcel_cargo_router.post(
    "/add",
    response_model=ParcelCargoResponseSchema,
    summary="Добавить груз к накладной",
    status_code=status.HTTP_201_CREATED,
)
async def add_parcel_cargo(
    data: ParcelCargoCreateSchema,
    _: dict = Depends(require_permission_in_context("add_parcel_cargo")),
):
    await validate_exists(Parcel, data.parcel_id, "Накладная")

    volume = data.length * data.height * data.weight
    total_volume = volume * data.quantity
    total_weight = data.weight * data.quantity

    create_data = data.model_dump()
    create_data.update(
        {
            "volume": volume,
            "total_volume": total_volume,
            "total_weight": total_weight,
        }
    )

    cargo = await ParcelCargo.create(**create_data)
    return ParcelCargoResponseSchema(cargo_id=cargo.id)


@parcel_cargo_router.patch(
    "/{cargo_id}",
    response_model=ParcelCargoResponseSchema,
    summary="Редактирование груза накладной",
)
async def edit_parcel_cargo(
    cargo_id: UUID,
    data: ParcelCargoEditSchema,
    _: dict = Depends(require_permission_in_context("edit_parcel_cargo")),
):
    cargo = await ParcelCargo.filter(id=cargo_id).first()

    if not cargo:
        raise HTTPException(status_code=404, detail="Груз не найден")

    update_data = data.model_dump(exclude_unset=True)

    # Пересчёт объемов и веса, если изменились параметры
    if {"length", "height", "weight", "quantity"} & update_data.keys():
        length = update_data.get("length", cargo.length)
        height = update_data.get("height", cargo.height)
        weight = update_data.get("weight", cargo.weight)
        quantity = update_data.get("quantity", cargo.quantity)

        volume = length * height * weight
        total_volume = volume * quantity
        total_weight = weight * quantity

        update_data.update(
            {
                "volume": volume,
                "total_volume": total_volume,
                "total_weight": total_weight,
            }
        )

    await cargo.update_from_dict(update_data)
    await cargo.save()

    return ParcelCargoResponseSchema(cargo_id=cargo.id)


@parcel_cargo_router.delete(
    "/{cargo_id}",
    summary="Удаление груза накладной",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_parcel_cargo(
    cargo_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_parcel_cargo")),
):
    cargo = await ParcelCargo.filter(id=cargo_id).first()

    if not cargo:
        raise HTTPException(status_code=404, detail="Груз не найден")

    await cargo.delete()
    return


@parcel_cargo_router.get(
    "/all",
    response_model=ParcelCargoListResponseSchema,
    summary="Получение списка грузов накладных",
)
async def get_parcel_cargo(
    filters: dict = Depends(parcel_cargo_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_parcel_cargo")),
):
    query = Q()

    if filters.get("parcel_id"):
        query &= Q(parcel_id=filters["parcel_id"])

    if filters.get("cargo_type"):
        query &= Q(cargo_type__icontains=filters["cargo_type"])

    sort_by = filters.get("sort_by", "cargo_type")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await ParcelCargo.filter(query).count()
    cargo = (
        await ParcelCargo.filter(query)
        .order_by(sort_field)
        .offset(offset)
        .limit(page_size)
    )

    return ParcelCargoListResponseSchema(
        total=total_count,
        cargo=[
            ParcelCargoSchema.model_validate(obj, from_attributes=True) for obj in cargo
        ],
    )


@parcel_cargo_router.get(
    "/{cargo_id}",
    response_model=ParcelCargoSchema,
    summary="Просмотр одного груза накладной",
)
async def get_parcel_cargo_by_id(
    cargo_id: UUID,
    _: dict = Depends(require_permission_in_context("view_parcel_cargo")),
):
    cargo = await ParcelCargo.filter(id=cargo_id).first()

    if not cargo:
        raise HTTPException(status_code=404, detail="Груз не найден")

    return ParcelCargoSchema.model_validate(cargo, from_attributes=True)
