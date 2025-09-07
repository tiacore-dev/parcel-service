from decimal import ROUND_HALF_UP, Decimal
from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from tiacore_lib.config import get_settings
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Parcel, ParcelCargo
from app.handlers.parcel_totals import recompute_parcel_totals
from app.handlers.service_updater import recompute_services_for_parcel
from app.pydantic_models.parcel_cargo_models import (
    ParcelCargoCreateSchema,
    ParcelCargoEditSchema,
    ParcelCargoListResponseSchema,
    ParcelCargoResponseSchema,
    ParcelCargoSchema,
    parcel_cargo_filter_params,
)

parcel_cargo_router = APIRouter()


MILLION = Decimal("1000000")


NumberLike = Union[Decimal, float, int, str]


def _to_dec(x: NumberLike) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def _q2(x: NumberLike) -> Decimal:
    return _to_dec(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _q9(x: NumberLike) -> Decimal:
    return _to_dec(x).quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)


@parcel_cargo_router.post(
    "/add",
    response_model=ParcelCargoResponseSchema,
    summary="Добавить груз к накладной",
    status_code=status.HTTP_201_CREATED,
)
async def add_parcel_cargo(
    request: Request,
    data: ParcelCargoCreateSchema,
    settings=Depends(get_settings),
    context: dict = Depends(require_permission_in_context("add_parcel_cargo")),
):
    parcel = await Parcel.get_or_none(id=data.parcel_id)
    if not parcel:
        raise HTTPException(status_code=400, detail="Накладная не найдена")

    # считаем аккуратно в Decimal
    length = Decimal(str(data.length))
    height = Decimal(str(data.height))
    width = Decimal(str(data.width))
    weight1 = Decimal(str(data.weight))
    qty = Decimal(str(data.quantity))

    volume = (length * height * width) / MILLION
    total_volume = volume * qty
    total_weight = weight1 * qty

    create_data = data.model_dump()
    create_data.update(
        {
            "volume": _q9(volume),  # под Decimal(..., 9)
            "total_volume": _q9(total_volume),
            "total_weight": _q2(total_weight),
        }
    )

    cargo = await ParcelCargo.create(created_by=context["user_id"], modified_by=context["user_id"], **create_data)

    # ✅ единый пересчёт сводных полей Parcel
    await recompute_parcel_totals(parcel.id)
    # ✅ пересчёт base_value + суммы услуг
    await recompute_services_for_parcel(settings, request, parcel.id, modified_by=context["user_id"])

    return ParcelCargoResponseSchema(cargo_id=cargo.id)


@parcel_cargo_router.patch(
    "/{cargo_id}",
    response_model=ParcelCargoResponseSchema,
    summary="Редактирование груза накладной",
)
async def edit_parcel_cargo(
    request: Request,
    cargo_id: UUID,
    data: ParcelCargoEditSchema,
    settings=Depends(get_settings),
    context: dict = Depends(require_permission_in_context("edit_parcel_cargo")),
):
    cargo = await ParcelCargo.filter(id=cargo_id).prefetch_related("parcel").first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Груз не найден")

    parcel = await Parcel.get_or_none(id=cargo.parcel.id)
    if not parcel:
        raise HTTPException(status_code=400, detail="Накладная не найдена")

    update_data = data.model_dump(exclude_unset=True)

    # если изменились габариты/вес/кол-во — пересчитать производные поля груза
    if {"length", "height", "width", "weight", "quantity"} & set(update_data.keys()):
        length = Decimal(str(update_data.get("length", cargo.length)))
        height = Decimal(str(update_data.get("height", cargo.height)))
        width = Decimal(str(update_data.get("width", cargo.width)))  # <-- фикс
        weight1 = Decimal(str(update_data.get("weight", cargo.weight)))
        qty = Decimal(str(update_data.get("quantity", cargo.quantity)))

        volume = (length * height * width) / MILLION
        total_volume = volume * qty
        total_weight = weight1 * qty

        update_data.update(
            {
                "volume": _q9(volume),  # под Decimal(..., 9)
                "total_volume": _q9(total_volume),
                "total_weight": _q2(total_weight),
            }
        )

    await cargo.update_from_dict(update_data)
    cargo.modified_by = context["user_id"]
    await cargo.save()

    # ✅ единый пересчёт сводных полей Parcel
    await recompute_parcel_totals(parcel.id)
    # ✅ пересчёт base_value + суммы услуг
    await recompute_services_for_parcel(settings, request, parcel.id, modified_by=context["user_id"])

    return ParcelCargoResponseSchema(cargo_id=cargo.id)


@parcel_cargo_router.delete(
    "/{cargo_id}",
    summary="Удаление груза накладной",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_parcel_cargo(
    request: Request,
    cargo_id: UUID,
    settings=Depends(get_settings),
    context: dict = Depends(require_permission_in_context("delete_parcel_cargo")),
):
    cargo = await ParcelCargo.filter(id=cargo_id).prefetch_related("parcel").first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Груз не найден")

    parcel_id = cargo.parcel.id
    await cargo.delete()

    # ✅ единый пересчёт сводных полей Parcel
    await recompute_parcel_totals(parcel_id)
    # ✅ пересчёт base_value + суммы услуг
    await recompute_services_for_parcel(settings, request, parcel_id, modified_by=context["user_id"])
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

    if filters.get("cargo_type_id"):
        query &= Q(cargo_type_id=filters["cargo_type_id"])

    sort_by = filters.get("sort_by", "created_at")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await ParcelCargo.filter(query).count()
    cargo = (
        await ParcelCargo.filter(query)
        .prefetch_related("cargo_type")
        .order_by(sort_field)
        .offset(offset)
        .limit(page_size)
    )

    return ParcelCargoListResponseSchema(
        total=total_count,
        cargo=[ParcelCargoSchema.model_validate(obj, from_attributes=True) for obj in cargo],
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
    cargo = await ParcelCargo.filter(id=cargo_id).prefetch_related("cargo_type").first()

    if not cargo:
        raise HTTPException(status_code=404, detail="Груз не найден")

    return ParcelCargoSchema.model_validate(cargo, from_attributes=True)
