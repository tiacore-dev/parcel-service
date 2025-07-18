from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from loguru import logger
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Attachments
from app.dependencies.permissions import with_permission_and_attachment_check
from app.pydantic_models.attachment_models import (
    AttachmentCreateSchema,
    AttachmentEditSchema,
    AttachmentListResponseSchema,
    AttachmentResponseSchema,
    AttachmentSchema,
    attachment_filter_params,
)
from app.s3.s3_manager import AsyncS3Manager

attachment_router = APIRouter()


@attachment_router.post(
    "/add",
    response_model=AttachmentResponseSchema,
    summary="Добавить вложение",
    status_code=status.HTTP_201_CREATED,
)
async def add_attachment(
    data: AttachmentCreateSchema = Depends(AttachmentCreateSchema.as_form),
    context: dict = Depends(require_permission_in_context("add_attachment")),
):
    if not context.get("is_superadmin") and str(data.company_id) != context["company_id"]:
        raise HTTPException(status_code=403, detail="Вы не имеете доступа к этой компании")

    file_bytes = await data.file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Не удалось загрузить данные файла")

    logger.info(
        f"""Тип загружаемых данных: {type(file_bytes)}, 
        размер: {len(file_bytes)} байт"""
    )

    filename = data.file.filename or "Unknown"
    manager = AsyncS3Manager()
    company_id = str(data.company_id) if data.company_id else "general"
    s3_key = await manager.upload_bytes(file_bytes, company_id, filename, entity="attachment")

    attachment = await Attachments.create(
        name=data.name,
        company_id=data.company_id,
        description=data.description,
        entity=data.entity,
        s3_key=s3_key,
    )
    return AttachmentResponseSchema(attachment_id=attachment.id)


@attachment_router.patch("/{attachment_id}", response_model=AttachmentResponseSchema, summary="Изменить вложение")
async def update_attachment(
    attachment_id: UUID,
    data: AttachmentEditSchema = Depends(AttachmentEditSchema.as_form),
    _=with_permission_and_attachment_check("edit_attachment"),
):
    attachment = await Attachments.filter(id=attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Вложение не найден")

    update_data = {}
    if attachment.company_id:
        company_id = attachment.company_id

        if data.company_id and data.company_id != attachment.company_id:
            update_data["company_id"] = data.company_id
            update_data.pop("company")
            company_id = data.company_id

    # Обновление файла
    if data.file and not isinstance(data.file, UploadFile):
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")

    if data.file:
        manager = AsyncS3Manager()
        file_bytes = await data.file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Не удалось загрузить файл")

        filename = data.file.filename or "Unknown"
        company_id_str = str(company_id) if company_id else ""

        await manager.delete_file(attachment.s3_key)
        new_s3_key = await manager.upload_bytes(file_bytes, company_id_str, filename, entity="attachment")
        update_data["s3_key"] = new_s3_key

    # Обновление прочих полей
    if data.name:
        update_data["name"] = data.name
    if data.description:
        update_data["description"] = data.description
    if data.entity:
        update_data["entity"] = data.entity

    await attachment.update_from_dict(update_data)
    await attachment.save()

    return AttachmentResponseSchema(attachment_id=attachment.id)


@attachment_router.delete("/{attachment_id}", summary="Удалить вложение", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(attachment_id: UUID, _=with_permission_and_attachment_check("delete_attachment")):
    attachment = await Attachments.filter(id=attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Вложение не найден")

    manager = AsyncS3Manager()
    await manager.delete_file(attachment.s3_key)

    await attachment.delete()


@attachment_router.get(
    "/all",
    response_model=AttachmentListResponseSchema,
    summary="Получение списка вложениеов",
)
async def get_attachments(
    filters: dict = Depends(attachment_filter_params),
    context=Depends(require_permission_in_context("get_all_attachments")),
):
    try:
        query = Q()
        if context["is_superadmin"]:
            company_filter = filters.get("company")
            if company_filter:
                query &= Q(company_id=company_filter) | Q(company_id=None)
        else:
            query &= Q(company_id=context["company_id"]) | Q(company_id=None)
        if filters.get("entity"):
            query &= Q(entity=filters["entity"])

        # ✅ Общее число записей
        total_count = await Attachments.filter(query).count()

        page = filters.get("page", 1)
        page_size = filters.get("page_size", 10)

        attachments = await Attachments.filter(query).offset((page - 1) * page_size).limit(page_size)

        return AttachmentListResponseSchema(
            total=total_count,
            attachments=[AttachmentSchema.model_validate(attachment) for attachment in attachments],
        )

    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@attachment_router.get("/{attachment_id}/download", summary="Скачивание вложения")
async def download_attachment(
    attachment_id: UUID,
    _=Depends(require_permission_in_context("download_attachment")),
):
    attachment = await Attachments.filter(id=attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Счет не найден")
    manager = AsyncS3Manager()
    url = await manager.generate_presigned_url(attachment.s3_key)
    return url


@attachment_router.get("/{attachment_id}", response_model=AttachmentSchema, summary="Просмотр одного счета")
async def get_attachment(attachment_id: UUID, _=Depends(require_permission_in_context("view_attachment"))):
    attachment = await Attachments.filter(id=attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Счет не найден")
    return AttachmentSchema.model_validate(attachment)
