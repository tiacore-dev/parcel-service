from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Parcel, ParcelProduct
from app.pydantic_models.parcel_products_models import (
    ParcelProductCreateSchema,
    ParcelProductEditSchema,
    ParcelProductListResponseSchema,
    ParcelProductResponseSchema,
    ParcelProductSchema,
    parcel_product_filter_params,
)

parcel_product_router = APIRouter()


@parcel_product_router.post(
    "/add",
    response_model=ParcelProductResponseSchema,
    summary="Добавить товар в накладную",
    status_code=status.HTTP_201_CREATED,
)
async def add_parcel_product(
    data: ParcelProductCreateSchema,
    _: dict = Depends(require_permission_in_context("add_parcel_product")),
):
    await validate_exists(Parcel, data.parcel_id, "Накладная")
    create_data = data.model_dump()
    create_data["summ"] = create_data["quantity"] * create_data["price"]
    product = await ParcelProduct.create(**create_data)
    return ParcelProductResponseSchema(product_id=product.id)


@parcel_product_router.patch(
    "/{product_id}",
    response_model=ParcelProductResponseSchema,
    summary="Редактирование товара накладной",
)
async def edit_parcel_product(
    product_id: UUID,
    data: ParcelProductEditSchema,
    _: dict = Depends(require_permission_in_context("edit_parcel_product")),
):
    product = await ParcelProduct.filter(id=product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    update_data = data.model_dump(exclude_unset=True)
    if "quantity" in update_data or "price" in update_data:
        quantity = update_data.get("quantity", product.quantity)
        price = update_data.get("price", product.price)
        update_data["summ"] = quantity * price

    await product.update_from_dict(update_data)
    await product.save()

    return ParcelProductResponseSchema(product_id=product.id)


@parcel_product_router.delete(
    "/{product_id}",
    summary="Удаление товара накладной",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_parcel_product(
    product_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_parcel_product")),
):
    product = await ParcelProduct.filter(id=product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    await product.delete()
    return


@parcel_product_router.get(
    "/all",
    response_model=ParcelProductListResponseSchema,
    summary="Получение списка товаров накладных",
)
async def get_parcel_products(
    filters: dict = Depends(parcel_product_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_parcel_products")),
):
    query = Q()

    if filters.get("parcel_id"):
        query &= Q(parcel_id=filters["parcel_id"])

    if filters.get("article_number"):
        query &= Q(article_number__icontains=filters["article_number"])

    if filters.get("delivered") is not None:
        query &= Q(delivered=filters["delivered"])

    sort_by = filters.get("sort_by", "name")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await ParcelProduct.filter(query).count()
    products = (
        await ParcelProduct.filter(query)
        .order_by(sort_field)
        .offset(offset)
        .limit(page_size)
    )

    return ParcelProductListResponseSchema(
        total=total_count,
        products=[
            ParcelProductSchema.model_validate(obj, from_attributes=True)
            for obj in products
        ],
    )


@parcel_product_router.get(
    "/{product_id}",
    response_model=ParcelProductSchema,
    summary="Просмотр одного товара накладной",
)
async def get_parcel_product_by_id(
    product_id: UUID,
    _: dict = Depends(require_permission_in_context("view_parcel_product")),
):
    product = await ParcelProduct.filter(id=product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    return ParcelProductSchema.model_validate(product, from_attributes=True)
