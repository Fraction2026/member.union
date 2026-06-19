import os
import uuid

import pytest
import requests


# Retirement schedule, member retirement calculation, search/filters, reports, and classifications tests
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
ADMIN_USERNAME = os.environ.get("TEST_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "admin123")


@pytest.fixture(scope="session")
def api_client():
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    return session


@pytest.fixture(scope="session")
def auth_headers(api_client):
    if not BASE_URL:
        pytest.skip("REACT_APP_BACKEND_URL is missing")

    response = api_client.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=20,
    )
    if response.status_code != 200:
        pytest.skip("Authentication failed - skipping authenticated tests")

    data = response.json()
    token = data.get("token")
    assert isinstance(token, str) and token
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def upload_doc_id(api_client, auth_headers):
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x03\x00\x01h&Y\r\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("retirement_test.png", png_bytes, "image/png")}
    response = api_client.post(f"{BASE_URL}/api/documents/upload", headers={"Authorization": auth_headers["Authorization"]}, files=files, timeout=30)
    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "image/png"
    assert isinstance(data.get("id"), str) and data["id"]
    return data["id"]


@pytest.fixture(scope="session")
def default_department_id(api_client, auth_headers):
    response = api_client.get(f"{BASE_URL}/api/departments", headers=auth_headers, timeout=20)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    target = next((item for item in data if item.get("name") == "مشروع التكافل الاجتماعي"), None)
    assert target is not None
    assert isinstance(target.get("id"), str) and target["id"]
    return target["id"]


def create_member(api_client, auth_headers, department_id, document_id, payload_overrides):
    base = {
        "department_id": department_id,
        "document_id": document_id,
        "governorate": "القاهرة",
        "union_committee": "لجنة اختبار",
        "membership_number": f"TEST-M-{uuid.uuid4().hex[:8]}",
        "name": f"TEST عضو {uuid.uuid4().hex[:6]}",
        "national_id": f"2{uuid.uuid4().int % 10**13:013d}",
        "birth_date": "1990-01-01",
        "address_phone": "القاهرة - 01000000000",
        "status": "فعال",
        "status_date": "2026-02-01",
        "address": "القاهرة",
    }
    body = {**base, **payload_overrides}
    response = api_client.post(f"{BASE_URL}/api/members", headers=auth_headers, json=body, timeout=25)
    assert response.status_code == 200
    return response.json(), body


def test_admin_retirement_schedule_get_put_persists_five_rows(api_client, auth_headers):
    get_response = api_client.get(f"{BASE_URL}/api/admin/retirement-schedule", headers=auth_headers, timeout=20)
    assert get_response.status_code == 200
    existing = get_response.json()
    assert isinstance(existing, list)
    assert len(existing) == 5

    put_payload = [
        {"effective_date": "1900-01-01", "retirement_age": 60, "description": "حتى يونيو 2032"},
        {"effective_date": "2032-07-01", "retirement_age": 61, "description": "يوليو 2032"},
        {"effective_date": "2034-07-01", "retirement_age": 62, "description": "يوليو 2034"},
        {"effective_date": "2036-07-01", "retirement_age": 63, "description": "يوليو 2036"},
        {"effective_date": "2040-07-01", "retirement_age": 65, "description": "يوليو 2040"},
    ]
    put_response = api_client.put(f"{BASE_URL}/api/admin/retirement-schedule", headers=auth_headers, json=put_payload, timeout=20)
    assert put_response.status_code == 200
    saved = put_response.json()
    assert len(saved) == 5
    assert saved[1]["retirement_age"] == 61

    get_after = api_client.get(f"{BASE_URL}/api/admin/retirement-schedule", headers=auth_headers, timeout=20)
    assert get_after.status_code == 200
    persisted = get_after.json()
    assert len(persisted) == 5
    assert [row["effective_date"] for row in persisted] == [row["effective_date"] for row in put_payload]


def test_member_creation_calculates_retirement_due_for_old_and_recent_birth_dates(api_client, auth_headers, default_department_id, upload_doc_id):
    old_member, _ = create_member(
        api_client,
        auth_headers,
        default_department_id,
        upload_doc_id,
        {
            "name": f"TEST قديم {uuid.uuid4().hex[:6]}",
            "birth_date": "1955-01-01",
            "membership_number": f"TEST-OLD-{uuid.uuid4().hex[:6]}",
        },
    )
    assert old_member["retirement_due"] is True
    assert old_member["retirement_date"] == "2015-01-01"

    recent_member, _ = create_member(
        api_client,
        auth_headers,
        default_department_id,
        upload_doc_id,
        {
            "name": f"TEST حديث {uuid.uuid4().hex[:6]}",
            "birth_date": "2000-01-01",
            "membership_number": f"TEST-NEW-{uuid.uuid4().hex[:6]}",
        },
    )
    assert recent_member["retirement_due"] is False
    assert recent_member["retirement_age"] == 65
    assert recent_member["retirement_date"] == "2065-01-01"


def test_members_search_restricted_to_name_or_national_id_and_supports_requested_filters(api_client, auth_headers, default_department_id, upload_doc_id):
    unique = uuid.uuid4().hex[:8]
    target_name = f"TEST بحث {unique}"
    target_nid = f"2{uuid.uuid4().int % 10**13:013d}"
    target_membership = f"TEST-MEMBER-{unique}"
    _, created_payload = create_member(
        api_client,
        auth_headers,
        default_department_id,
        upload_doc_id,
        {
            "name": target_name,
            "national_id": target_nid,
            "membership_number": target_membership,
            "governorate": "الإسكندرية",
            "union_committee": "لجنة البحري",
            "birth_date": "1950-05-01",
        },
    )

    by_name = api_client.get(
        f"{BASE_URL}/api/members?department_id={default_department_id}&search={target_name}",
        headers=auth_headers,
        timeout=25,
    )
    assert by_name.status_code == 200
    data_by_name = by_name.json()
    assert any(item.get("name") == target_name for item in data_by_name)

    by_nid = api_client.get(
        f"{BASE_URL}/api/members?department_id={default_department_id}&search={target_nid}",
        headers=auth_headers,
        timeout=25,
    )
    assert by_nid.status_code == 200
    data_by_nid = by_nid.json()
    assert any(item.get("national_id") == target_nid for item in data_by_nid)

    by_membership_number = api_client.get(
        f"{BASE_URL}/api/members?department_id={default_department_id}&search={target_membership}",
        headers=auth_headers,
        timeout=25,
    )
    assert by_membership_number.status_code == 200
    data_by_membership = by_membership_number.json()
    assert not any(item.get("membership_number") == target_membership for item in data_by_membership)

    with_filters = api_client.get(
        f"{BASE_URL}/api/members?department_id={default_department_id}&governorate={created_payload['governorate']}&union_committee={created_payload['union_committee']}&retirement_due=true",
        headers=auth_headers,
        timeout=25,
    )
    assert with_filters.status_code == 200
    filtered = with_filters.json()
    target = next((item for item in filtered if item.get("membership_number") == target_membership), None)
    assert target is not None
    assert target["retirement_due"] is True


def test_membership_reports_returns_expected_aggregates(api_client, auth_headers, default_department_id):
    response = api_client.get(f"{BASE_URL}/api/reports/membership?department_id={default_department_id}", headers=auth_headers, timeout=25)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("total_members"), int)
    assert isinstance(data.get("retirement_due_count"), int)
    assert isinstance(data.get("by_governorate"), list)
    assert isinstance(data.get("by_union_committee"), list)
    if data["by_governorate"]:
        first = data["by_governorate"][0]
        assert isinstance(first.get("name"), str)
        assert isinstance(first.get("count"), int)


def test_classifications_returns_governorates_and_union_committees(api_client, auth_headers, default_department_id):
    response = api_client.get(f"{BASE_URL}/api/classifications?department_id={default_department_id}", headers=auth_headers, timeout=25)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("governorates"), list)
    assert isinstance(data.get("union_committees"), list)
