from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import IssueToEmployee, Parcel, ParcelStatus, ParcelStatusEnum
from app.handlers.status_handler import recalculate_parcel_status
from app.pydantic_models.issue_to_employee_models import (
    IssueToEmployeeCreateSchema,
    IssueToEmployeeEditSchema,
    IssueToEmployeeListResponseSchema,
    IssueToEmployeeResponseSchema,
    IssueToEmployeeSchema,
    issue_to_employee_filter_params,
)

issue_to_employee_router = APIRouter()


@issue_to_employee_router.post(
    "/add",
    response_model=IssueToEmployeeResponseSchema,
    summary="Добавить событие выдачи сотруднику",
    status_code=status.HTTP_201_CREATED,
)
async def add_issue_to_employee(
    data: IssueToEmployeeCreateSchema,
    context: dict = Depends(require_permission_in_context("add_issue_to_employee")),
):
    await validate_exists(Parcel, data.parcel_id, "Накладная")
    issue = await IssueToEmployee.create(
        created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump()
    )
    await ParcelStatus.create(
        parcel_id=data.parcel_id,
        document_id=issue.id,
        document_type="issue_id",
        status=ParcelStatusEnum.WITH_EMPLOYEE,
        date=data.date,
        value=data.employee_id,
        value_type="user_id",
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(data.parcel_id)
    return IssueToEmployeeResponseSchema(issue_id=issue.id)


@issue_to_employee_router.get(
    "/all",
    response_model=IssueToEmployeeListResponseSchema,
    summary="Получение списка выдач сотруднику",
)
async def get_issue_to_employee_list(
    filters: dict = Depends(issue_to_employee_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_issues_to_employee")),
):
    query = Q()

    if filters.get("parcel_id"):
        query &= Q(parcel_id=filters["parcel_id"])

    if filters.get("employee_id"):
        query &= Q(employee_id=filters["employee_id"])

    if filters.get("date_from"):
        query &= Q(date__gte=filters["date_from"])

    if filters.get("date_to"):
        query &= Q(date__lte=filters["date_to"])

    sort_by = filters.get("sort_by", "date")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await IssueToEmployee.filter(query).count()
    issues = await IssueToEmployee.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return IssueToEmployeeListResponseSchema(
        total=total_count,
        issues=[IssueToEmployeeSchema.model_validate(obj, from_attributes=True) for obj in issues],
    )


@issue_to_employee_router.get(
    "/{issue_id}",
    response_model=IssueToEmployeeSchema,
    summary="Просмотр одного события выдачи сотруднику",
)
async def get_issue_to_employee(
    issue_id: UUID,
    _: dict = Depends(require_permission_in_context("view_issue_to_employee")),
):
    issue = await IssueToEmployee.filter(id=issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    return IssueToEmployeeSchema.model_validate(issue, from_attributes=True)


@issue_to_employee_router.patch(
    "/{issue_id}",
    response_model=IssueToEmployeeResponseSchema,
    summary="Редактирование события выдачи сотруднику",
)
async def edit_issue_to_employee(
    issue_id: UUID,
    data: IssueToEmployeeEditSchema,
    context: dict = Depends(require_permission_in_context("edit_issue_to_employee")),
):
    issue = await IssueToEmployee.filter(id=issue_id).prefetch_related("parcel").first()

    if not issue:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    await issue.update_from_dict(data.model_dump(exclude_unset=True))
    issue.modified_by = context["user_id"]
    await issue.save()
    await ParcelStatus.filter(document_id=issue_id).delete()
    await ParcelStatus.create(
        parcel_id=issue.parcel.id,
        document_id=issue.id,
        document_type="issue_id",
        status=ParcelStatusEnum.WITH_EMPLOYEE,
        date=issue.date,
        value=issue.employee_id,
        value_type="user_id",
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(issue.parcel.id)

    return IssueToEmployeeResponseSchema(issue_id=issue.id)


@issue_to_employee_router.delete(
    "/{issue_id}",
    summary="Удаление события выдачи сотруднику",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_issue_to_employee(
    issue_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_issue_to_employee")),
):
    issue = await IssueToEmployee.filter(id=issue_id).prefetch_related("parcel").first()

    if not issue:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    await ParcelStatus.filter(document_id=issue_id).delete()
    await recalculate_parcel_status(issue.parcel.id)
    await issue.delete()

    return
