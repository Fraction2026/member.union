import os
import uuid

import pytest
import requests


# Core auth, departments, scanner config, document upload, and members flow tests
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


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
        json={"username": "admin", "password": "admin123"},
        timeout=20,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("token"), str) and data["token"]
    return {"Authorization": f"Bearer {data['token']}"}


@pytest.fixture(scope="session")
def uploaded_document_id(api_client, auth_headers):
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x03\x00\x01h&Y\r\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("test_member.png", png_bytes, "image/png")}
    response = api_client.post(
        f"{BASE_URL}/api/documents/upload",
        headers=auth_headers,
        files=files,
        timeout=30,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["original_name"] == "test_member.png"
    assert data["content_type"] == "image/png"
    assert isinstance(data.get("id"), str) and data["id"]
    return data["id"]


def test_auth_login_success_and_me(api_client, auth_headers):
    me_response = api_client.get(
        f"{BASE_URL}/api/auth/me",
        headers=auth_headers,
        timeout=20,
    )
    assert me_response.status_code == 200
    me = me_response.json()
    assert me["username"] == "admin"
    assert me["role"] == "admin"


def test_departments_list_contains_default_project(api_client, auth_headers):
    response = api_client.get(
        f"{BASE_URL}/api/departments",
        headers=auth_headers,
        timeout=20,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item.get("name") == "مشروع التكافل الاجتماعي" for item in data)


def test_admin_can_add_department_and_verify_persistence(api_client, auth_headers):
    unique_suffix = uuid.uuid4().hex[:8]
    payload = {
        "name": f"إدارة اختبار API {unique_suffix}",
        "code": f"API{unique_suffix}",
        "description": "إدارة للاختبار الآلي",
        "active": True,
    }
    create_response = api_client.post(
        f"{BASE_URL}/api/departments",
        headers={**auth_headers, "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["name"] == payload["name"]
    assert created["code"] == payload["code"]

    list_response = api_client.get(
        f"{BASE_URL}/api/departments",
        headers=auth_headers,
        timeout=20,
    )
    assert list_response.status_code == 200
    listed = list_response.json()
    found = next((item for item in listed if item["id"] == created["id"]), None)
    assert found is not None
    assert found["name"] == payload["name"]


def test_scanner_config_save_and_get(api_client, auth_headers):
    unique = uuid.uuid4().hex[:6]
    payload = {
        "connection_name": f"Test Scanner {unique}",
        "protocol": "escl",
        "host": "",
        "port": 80,
        "base_path": "/eSCL",
        "use_tls": False,
        "adf_enabled": True,
        "color_mode": "Color",
        "resolution_dpi": 300,
        "paper_size": "A4",
    }
    save_response = api_client.put(
        f"{BASE_URL}/api/admin/scanner-config",
        headers={**auth_headers, "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    assert save_response.status_code == 200
    saved = save_response.json()
    assert saved["connection_name"] == payload["connection_name"]
    assert saved["protocol"] == payload["protocol"]

    get_response = api_client.get(
        f"{BASE_URL}/api/admin/scanner-config",
        headers=auth_headers,
        timeout=20,
    )
    assert get_response.status_code == 200
    got = get_response.json()
    assert got["connection_name"] == payload["connection_name"]
    assert got["base_path"] == payload["base_path"]


def test_scanner_test_returns_clear_error_when_host_missing(api_client, auth_headers):
    save_response = api_client.put(
        f"{BASE_URL}/api/admin/scanner-config",
        headers={**auth_headers, "Content-Type": "application/json"},
        json={
            "connection_name": "No Host",
            "protocol": "escl",
            "host": "",
            "port": 80,
            "base_path": "/eSCL",
            "use_tls": False,
            "adf_enabled": True,
            "color_mode": "Color",
            "resolution_dpi": 300,
            "paper_size": "A4",
        },
        timeout=20,
    )
    assert save_response.status_code == 200

    test_response = api_client.post(
        f"{BASE_URL}/api/admin/scanner-test",
        headers=auth_headers,
        timeout=20,
    )
    assert test_response.status_code == 400
    assert "أدخل عنوان" in test_response.json().get("detail", "")


def test_scanner_test_returns_clear_error_when_unreachable_host(api_client, auth_headers):
    save_response = api_client.put(
        f"{BASE_URL}/api/admin/scanner-config",
        headers={**auth_headers, "Content-Type": "application/json"},
        json={
            "connection_name": "Unreachable Host",
            "protocol": "escl",
            "host": "192.0.2.10",
            "port": 80,
            "base_path": "/eSCL",
            "use_tls": False,
            "adf_enabled": True,
            "color_mode": "Color",
            "resolution_dpi": 300,
            "paper_size": "A4",
        },
        timeout=20,
    )
    assert save_response.status_code == 200

    test_response = api_client.post(
        f"{BASE_URL}/api/admin/scanner-test",
        headers=auth_headers,
        timeout=20,
    )
    assert test_response.status_code == 400
    assert "تعذر الوصول" in test_response.json().get("detail", "")


def test_member_create_duplicate_protection_and_listing(api_client, auth_headers, uploaded_document_id):
    departments_response = api_client.get(
        f"{BASE_URL}/api/departments",
        headers=auth_headers,
        timeout=20,
    )
    assert departments_response.status_code == 200
    departments = departments_response.json()
    department_id = next((d["id"] for d in departments if d.get("name") == "مشروع التكافل الاجتماعي"), None)
    assert department_id is not None

    unique = uuid.uuid4().hex[:8]
    payload = {
        "department_id": department_id,
        "document_id": uploaded_document_id,
        "governorate": "القاهرة",
        "union_committee": "لجنة الاختبار",
        "membership_number": f"MEM-{unique}",
        "name": f"عضو اختبار {unique}",
        "national_id": f"2{uuid.uuid4().int % 10**13:013d}",
        "birth_date": "1990-01-01",
        "address_phone": "العنوان - 01000000000",
        "status": "فعال",
        "status_date": "2026-02-01",
        "address": "القاهرة",
    }

    create_response = api_client.post(
        f"{BASE_URL}/api/members",
        headers={**auth_headers, "Content-Type": "application/json"},
        json=payload,
        timeout=25,
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["name"] == payload["name"]
    assert created["membership_number"] == payload["membership_number"]
    assert created["document_url"].startswith("/api/documents/")

    duplicate_response = api_client.post(
        f"{BASE_URL}/api/members",
        headers={**auth_headers, "Content-Type": "application/json"},
        json=payload,
        timeout=25,
    )
    assert duplicate_response.status_code == 409
    assert "يوجد عضو" in duplicate_response.json().get("detail", "")

    list_response = api_client.get(f"{BASE_URL}/api/members?department_id={department_id}", headers=auth_headers, timeout=25)
    assert list_response.status_code == 200
    listed = list_response.json()
    matching = [m for m in listed if m.get("membership_number") == payload["membership_number"]]
    assert len(matching) == 1
    assert matching[0]["document_url"].startswith("/api/documents/")


def test_national_id_duplicate_should_be_allowed_across_departments_per_requirement(api_client, auth_headers, uploaded_document_id):
    unique_suffix = uuid.uuid4().hex[:7]
    dep_payload_1 = {
        "name": f"قسم قواعد تكرار 1 {unique_suffix}",
        "code": f"DUP1{unique_suffix}",
        "description": "اختبار تكرار الرقم القومي بين إدارتين",
        "active": True,
    }
    dep_payload_2 = {
        "name": f"قسم قواعد تكرار 2 {unique_suffix}",
        "code": f"DUP2{unique_suffix}",
        "description": "اختبار تكرار الرقم القومي بين إدارتين",
        "active": True,
    }

    dep1_response = api_client.post(
        f"{BASE_URL}/api/departments",
        headers={**auth_headers, "Content-Type": "application/json"},
        json=dep_payload_1,
        timeout=20,
    )
    assert dep1_response.status_code == 200
    dep1_id = dep1_response.json()["id"]

    dep2_response = api_client.post(
        f"{BASE_URL}/api/departments",
        headers={**auth_headers, "Content-Type": "application/json"},
        json=dep_payload_2,
        timeout=20,
    )
    assert dep2_response.status_code == 200
    dep2_id = dep2_response.json()["id"]

    shared_national_id = f"2{uuid.uuid4().int % 10**13:013d}"

    member_1 = {
        "department_id": dep1_id,
        "document_id": uploaded_document_id,
        "governorate": "الجيزة",
        "union_committee": "لجنة 1",
        "membership_number": f"M1-{unique_suffix}",
        "name": f"عضو إدارة أولى {unique_suffix}",
        "national_id": shared_national_id,
        "birth_date": "1992-02-02",
        "address_phone": "عنوان 1",
        "status": "فعال",
        "status_date": "2026-02-01",
        "address": "الجيزة",
    }
    create_1 = api_client.post(
        f"{BASE_URL}/api/members",
        headers={**auth_headers, "Content-Type": "application/json"},
        json=member_1,
        timeout=25,
    )
    assert create_1.status_code == 200

    member_2 = {
        **member_1,
        "department_id": dep2_id,
        "membership_number": f"M2-{unique_suffix}",
        "name": f"عضو إدارة ثانية {unique_suffix}",
    }
    create_2 = api_client.post(
        f"{BASE_URL}/api/members",
        headers={**auth_headers, "Content-Type": "application/json"},
        json=member_2,
        timeout=25,
    )

    # Requirement: duplicates should be blocked only within the same department.
    assert create_2.status_code == 200
