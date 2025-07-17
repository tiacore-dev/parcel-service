from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import IssueToEmployee, Parcel


@pytest.mark.asyncio
async def test_add_issue_to_employee(test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "employee_id": str(uuid4()),
        "date": datetime.now().isoformat(),
        "parcel_id": str(seed_parcel.id),
    }

    response = await test_app.post("/api/issue-to-employee/add", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    issue = await IssueToEmployee.get_or_none(id=response_data["issue_id"]).prefetch_related("parcel")

    assert issue is not None
    assert issue.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_issue_to_employee(test_app: AsyncClient, jwt_token_admin, seed_issue_to_employee: IssueToEmployee):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "employee_id": str(uuid4()),
    }

    response = await test_app.patch(
        f"/api/issue-to-employee/{seed_issue_to_employee.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    updated_issue = await IssueToEmployee.get_or_none(id=seed_issue_to_employee.id)
    assert updated_issue is not None
    assert str(updated_issue.employee_id) == data["employee_id"]


@pytest.mark.asyncio
async def test_view_issue_to_employee(test_app: AsyncClient, jwt_token_admin, seed_issue_to_employee: IssueToEmployee):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/issue-to-employee/{seed_issue_to_employee.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["issue_id"] == str(seed_issue_to_employee.id)


@pytest.mark.asyncio
async def test_delete_issue_to_employee(
    test_app: AsyncClient, jwt_token_admin, seed_issue_to_employee: IssueToEmployee
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/issue-to-employee/{seed_issue_to_employee.id}",
        headers=headers,
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await IssueToEmployee.get_or_none(id=seed_issue_to_employee.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_issue_to_employee_list(
    test_app: AsyncClient, jwt_token_admin, seed_issue_to_employee: IssueToEmployee, seed_parcel: Parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/issue-to-employee/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    issues = data["issues"]

    assert data["total"] >= 1
    assert isinstance(issues, list)
    assert any(issue["issue_id"] == str(seed_issue_to_employee.id) for issue in issues)
    assert any(issue["parcel_name"] == seed_parcel.name for issue in issues)
