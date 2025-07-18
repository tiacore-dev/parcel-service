import pytest
from httpx import AsyncClient

from app.database.models import IssueDetails, Parcel


@pytest.mark.asyncio
async def test_add_issue_details(test_app: AsyncClient, jwt_token_admin, seed_issue, seed_parcel):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "issue_id": str(seed_issue.id),
        "parcel_id": str(seed_parcel.id),
    }

    response = await test_app.post("/api/issue-details/add", headers=headers, json=data)

    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    detail = await IssueDetails.get_or_none(id=response_data["details_id"]).prefetch_related("issue", "parcel")

    assert detail is not None
    assert detail.issue.id == seed_issue.id
    assert detail.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_edit_issue_details(
    test_app: AsyncClient,
    jwt_token_admin,
    seed_issue_details,
    seed_issue,
    seed_parcel,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    data = {
        "issue_id": str(seed_issue.id),
        "parcel_id": str(seed_parcel.id),
    }

    response = await test_app.patch(
        f"/api/issue-details/{seed_issue_details.id}",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    updated = await IssueDetails.get_or_none(id=seed_issue_details.id).prefetch_related("issue", "parcel")
    assert updated is not None
    assert updated.issue.id == seed_issue.id
    assert updated.parcel.id == seed_parcel.id


@pytest.mark.asyncio
async def test_view_issue_details(test_app: AsyncClient, jwt_token_admin, seed_issue_details: IssueDetails):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/issue-details/{seed_issue_details.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["details_id"] == str(seed_issue_details.id)


@pytest.mark.asyncio
async def test_delete_issue_details(test_app: AsyncClient, jwt_token_admin, seed_issue_details):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(f"/api/issue-details/{seed_issue_details.id}", headers=headers)

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    deleted = await IssueDetails.get_or_none(id=seed_issue_details.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_issue_details_list(
    test_app: AsyncClient, jwt_token_admin, seed_issue_details: IssueDetails, seed_parcel: Parcel
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/issue-details/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    details = data["details"]

    assert data["total"] >= 1
    assert isinstance(details, list)
    assert any(detail["details_id"] == str(seed_issue_details.id) for detail in details)
    assert any(detail["parcel_name"] == seed_parcel.name for detail in details)
