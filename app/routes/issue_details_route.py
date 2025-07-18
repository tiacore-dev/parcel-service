from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import (
    Issue,
    IssueDetails,
    Parcel,
    ParcelStatus,
    ParcelStatusEnum,
)
from app.handlers.status_handler import recalculate_parcel_status
from app.pydantic_models.issue_details_models import (
    IssueDetailsCreateSchema,
    IssueDetailsEditSchema,
    IssueDetailsListResponseSchema,
    IssueDetailsResponseSchema,
    IssueDetailsSchema,
    issue_details_filter_params,
)

issue_details_router = APIRouter()


@issue_details_router.post(
    "/add",
    response_model=IssueDetailsResponseSchema,
    summary="Добавить деталь транзита",
    status_code=status.HTTP_201_CREATED,
)
async def add_issue_details(
    data: IssueDetailsCreateSchema,
    context: dict = Depends(require_permission_in_context("add_issue_details")),
):
    issue = await Issue.get_or_none(id=data.issue_id)
    if not issue:
        raise HTTPException(status_code=400, detail="Транзита не существует")
    await validate_exists(Parcel, data.parcel_id, "Накладная")

    detail = await IssueDetails.create(
        created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump()
    )
    await ParcelStatus.create(
        parcel_id=data.parcel_id,
        document_id=issue.id,
        document_type="issue_id",
        status=ParcelStatusEnum.WITH_EMPLOYEE,
        date=issue.date,
        value=issue.employee_id,
        value_type="user_id",
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(data.parcel_id)
    return IssueDetailsResponseSchema(details_id=detail.id)


@issue_details_router.get(
    "/all",
    response_model=IssueDetailsListResponseSchema,
    summary="Получение списка деталей транзита",
)
async def get_issue_details_list(
    filters: dict = Depends(issue_details_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_issue_details")),
):
    query = Q()

    if filters.get("issue_id"):
        query &= Q(issue_id=filters["issue_id"])

    if filters.get("parcel_id"):
        query &= Q(parcel_id=filters["parcel_id"])

    if filters.get("parcel_name"):
        query &= Q(parcel__name__icontains=filters["parcel_name"])

    sort_by = filters.get("sort_by", "id")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await IssueDetails.filter(query).count()
    details = (
        await IssueDetails.filter(query).order_by(sort_field).offset(offset).limit(page_size).prefetch_related("parcel")
    )
    detail_schemas = []
    for detail in details:
        parcel = await Parcel.get_or_none(id=detail.parcel.id)
        if not parcel:
            raise HTTPException(status_code=400, detail="Накладная не найдена")
        parcel_data = {
            "parcel_name": parcel.name,
            "places_count": parcel.places_count,
            "recipient_city": parcel.recipient_city,
            "volume": parcel.volume,
            "weight": parcel.weight,
            "recipient_additional_info": parcel.recipient_additional_info,
        }
        detail_dict = detail.__dict__

        combined_data = {**detail_dict, **parcel_data}

        detail_schemas.append(IssueDetailsSchema.model_validate(combined_data))

    return IssueDetailsListResponseSchema(
        total=total_count,
        details=detail_schemas,
    )


@issue_details_router.get(
    "/{details_id}",
    response_model=IssueDetailsSchema,
    summary="Просмотр одной детали транзита",
)
async def get_issue_details(
    details_id: UUID,
    _: dict = Depends(require_permission_in_context("view_issue_details")),
):
    detail = await IssueDetails.filter(id=details_id).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")

    return IssueDetailsSchema.model_validate(detail, from_attributes=True)


@issue_details_router.patch(
    "/{details_id}",
    response_model=IssueDetailsResponseSchema,
    summary="Редактирование детали транзита",
)
async def edit_issue_details(
    details_id: UUID,
    data: IssueDetailsEditSchema,
    context: dict = Depends(require_permission_in_context("edit_issue_details")),
):
    detail = await IssueDetails.filter(id=details_id).prefetch_related("parcel", "issue").first()

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")

    await detail.update_from_dict(data.model_dump(exclude_unset=True))
    detail.modified_by = context["user_id"]
    await detail.save()
    await ParcelStatus.filter(document_id=detail.issue.id).delete()
    await ParcelStatus.create(
        parcel_id=detail.parcel.id,
        document_id=detail.issue.id,
        document_type="issue_id",
        status=ParcelStatusEnum.WITH_EMPLOYEE,
        date=detail.issue.date,
        value=detail.issue.employee_id,
        value_type="user_id",
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(detail.parcel.id)
    return IssueDetailsResponseSchema(details_id=detail.id)


@issue_details_router.delete(
    "/{details_id}",
    summary="Удаление детали транзита",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_issue_details(
    details_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_issue_details")),
):
    detail = await IssueDetails.filter(id=details_id).prefetch_related("parcel").first()

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")
    parcel_id = detail.parcel.id
    await detail.delete()
    await recalculate_parcel_status(parcel_id)
    return
