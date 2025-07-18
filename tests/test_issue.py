from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import Issue, IssueDetails, Parcel


@pytest.mark.asyncio
async def test_add_issue(test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "employee_id": str(uuid4()),
        "date": datetime.now().isoformat(),
    }

    response = await test_app.post("/api/issues/add", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    issue = await Issue.get_or_none(id=response_data["issue_id"])

    assert issue is not None


@pytest.mark.asyncio
async def test_add_issue_bulk(test_app: AsyncClient, jwt_token_admin, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {"employee_id": str(uuid4()), "date": datetime.now().isoformat(), "parcels": [str(seed_parcel.id)]}

    response = await test_app.post("/api/issues/add-bulk", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    issue = await Issue.get_or_none(id=response_data["issue_id"])

    detail = await IssueDetails.get_or_none(parcel_id=seed_parcel.id)
    assert issue is not None
    assert detail is not None


@pytest.mark.asyncio
async def test_edit_issue(test_app: AsyncClient, jwt_token_admin, seed_issue: Issue):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "employee_id": str(uuid4()),
    }

    response = await test_app.patch(
        f"/api/issues/{seed_issue.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    updated_issue = await Issue.get_or_none(id=seed_issue.id)
    assert updated_issue is not None
    assert str(updated_issue.employee_id) == data["employee_id"]


@pytest.mark.asyncio
async def test_view_issue(test_app: AsyncClient, jwt_token_admin, seed_issue: Issue):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/issues/{seed_issue.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["issue_id"] == str(seed_issue.id)


@pytest.mark.asyncio
async def test_delete_issue(test_app: AsyncClient, jwt_token_admin, seed_issue: Issue):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/issues/{seed_issue.id}",
        headers=headers,
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await Issue.get_or_none(id=seed_issue.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_issue_list(test_app: AsyncClient, jwt_token_admin, seed_issue: Issue, seed_parcel: Parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/issues/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    issues = data["issues"]

    assert data["total"] >= 1
    assert isinstance(issues, list)
    assert any(issue["issue_id"] == str(seed_issue.id) for issue in issues)
