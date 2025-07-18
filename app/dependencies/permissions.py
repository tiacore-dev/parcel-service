from uuid import UUID

from fastapi import Depends, HTTPException, Path
from tiacore_lib.handlers.dependency_handler import require_permission_in_context

from app.database.models import Attachments, Templates


def with_permission_and_template_check(permission: str):
    async def dependency(
        template_id: UUID = Path(..., description="ID шаблона"),
        context: dict = Depends(require_permission_in_context(permission)),
    ):
        if context.get("is_superadmin"):
            return context

        template = await Templates.get_or_none(id=template_id)

        if not template:
            raise HTTPException(
                status_code=403,
                detail="Шаблон не найден",
            )
        if template.company_id:
            if str(template.company_id) != str(context["company_id"]):
                raise HTTPException(
                    status_code=403,
                    detail="Шаблон не принадлежит указанной компании",
                )

        return context

    return Depends(dependency)


def with_permission_and_attachment_check(permission: str):
    async def dependency(
        attachment_id: UUID = Path(..., description="ID шаблона"),
        context: dict = Depends(require_permission_in_context(permission)),
    ):
        if context.get("is_superadmin"):
            return context

        attachment = await Attachments.get_or_none(id=attachment_id)

        if not attachment:
            raise HTTPException(
                status_code=403,
                detail="Шаблон не найден",
            )
        if attachment.company_id:
            if str(attachment.company_id) != str(context["company_id"]):
                raise HTTPException(
                    status_code=403,
                    detail="Шаблон не принадлежит указанной компании",
                )

        return context

    return Depends(dependency)
