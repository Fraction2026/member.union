"""Backend regression tests for:

  1. POST /api/aids/{aid_id}/recalculate
  2. POST /api/presence/heartbeat
  3. GET  /api/presence/online
  4. POST /api/presence/logout
  5. Regressions: GET /api/aids, GET /api/changes/state, recalc bumps aids counter

These tests hit the locally running FastAPI service via the public /api prefix.
"""
import os
import pytest
import requests

# Use the in-pod backend URL; ingress wraps the same routes externally.
BASE_URL = os.environ.get("INTERNAL_BACKEND_URL", "http://localhost:8001").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
MOSTAFA_USER = "mostafa"
MOSTAFA_PASS = "123456"
MOSTAFA_DISPLAY = "مصطفى السيد"


# ─── Fixtures ────────────────────────────────────────────────────────────────
def _login(username: str, password: str):
    r = requests.post(
        f"{API}/auth/login",
        json={"username": username, "password": password},
        timeout=15,
    )
    return r


@pytest.fixture(scope="module")
def admin_token():
    r = _login(ADMIN_USER, ADMIN_PASS)
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    body = r.json()
    return body["token"], body["user"]


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token[0]}"}


@pytest.fixture(scope="module")
def mostafa_token(admin_headers):
    """Ensure user 'mostafa' exists and return their login token."""
    # Try login first; if not present, create then login.
    r = _login(MOSTAFA_USER, MOSTAFA_PASS)
    if r.status_code == 200:
        body = r.json()
        return body["token"], body["user"]

    # Create as employee via admin.
    create = requests.post(
        f"{API}/admin/users",
        headers={**admin_headers, "Content-Type": "application/json"},
        json={
            "username": MOSTAFA_USER,
            "password": MOSTAFA_PASS,
            "display_name": MOSTAFA_DISPLAY,
            "role": "employee",
            "active": True,
            "portal_permissions": [],
        },
        timeout=15,
    )
    assert create.status_code in (200, 201), f"create mostafa failed: {create.status_code} {create.text}"
    r2 = _login(MOSTAFA_USER, MOSTAFA_PASS)
    assert r2.status_code == 200, f"mostafa login failed after create: {r2.status_code} {r2.text}"
    body = r2.json()
    return body["token"], body["user"]


@pytest.fixture(scope="module")
def department_id(admin_headers):
    r = requests.get(f"{API}/departments", headers=admin_headers, timeout=15)
    assert r.status_code == 200
    deps = r.json()
    assert deps, "no departments returned"
    return deps[0]["id"]


@pytest.fixture(scope="module")
def sample_aid(admin_headers, department_id):
    r = requests.get(
        f"{API}/aids",
        params={"department_id": department_id},
        headers=admin_headers,
        timeout=20,
    )
    assert r.status_code == 200, r.text
    aids = r.json()
    if not aids:
        pytest.skip("No aids seeded — cannot exercise recalculate endpoint")
    return aids[0]


# ─── Aid recalculate endpoint ───────────────────────────────────────────────
class TestAidRecalculate:
    def test_requires_authentication(self, sample_aid):
        r = requests.post(f"{API}/aids/{sample_aid['id']}/recalculate", timeout=15)
        assert r.status_code in (401, 403), f"expected 401/403, got {r.status_code}"

    def test_unknown_aid_returns_404(self, admin_headers):
        r = requests.post(
            f"{API}/aids/__definitely_not_an_aid__/recalculate",
            headers=admin_headers,
            timeout=15,
        )
        assert r.status_code == 404

    def test_recalculate_happy_path(self, admin_headers, sample_aid):
        aid_id = sample_aid["id"]
        r = requests.post(
            f"{API}/aids/{aid_id}/recalculate",
            headers=admin_headers,
            timeout=30,
        )
        assert r.status_code == 200, r.text
        body = r.json()

        # Top-level shape
        for k in ("ok", "aid", "committee_dues", "member_refreshed"):
            assert k in body, f"missing key '{k}' in recalc response: {body.keys()}"
        assert body["ok"] is True
        assert isinstance(body["aid"], dict)
        assert isinstance(body["committee_dues"], dict)
        assert isinstance(body["member_refreshed"], bool)

        # FINANCIAL_START_MONTH floor honoured
        from_month = body["committee_dues"].get("from_month", "")
        assert from_month >= "2025-01", f"committee_dues.from_month {from_month!r} violates 2025-01 floor"

        # Member snapshot fields aligned with the latest member doc.
        aid = body["aid"]
        member_id = aid.get("member_id")
        if member_id and body["member_refreshed"]:
            mres = requests.get(
                f"{API}/members/{member_id}",
                headers=admin_headers,
                timeout=15,
            )
            assert mres.status_code == 200, mres.text
            m = mres.json()
            assert aid.get("member_name") == m.get("name", "")
            assert aid.get("member_governorate") == m.get("governorate", "")
            assert aid.get("member_subscription_date") == m.get("subscription_date", "")
            assert aid.get("member_status_date") == m.get("status_date", "")


# ─── Presence indicator: heartbeat / online / logout ─────────────────────────
class TestPresence:
    def test_heartbeat_requires_auth(self):
        r = requests.post(
            f"{API}/presence/heartbeat",
            json={"path": "/x", "page_title": "X"},
            timeout=15,
        )
        assert r.status_code in (401, 403)

    def test_online_requires_auth(self):
        r = requests.get(f"{API}/presence/online", timeout=15)
        assert r.status_code in (401, 403)

    def test_heartbeat_returns_ok_ts(self, admin_headers):
        r = requests.post(
            f"{API}/presence/heartbeat",
            headers=admin_headers,
            json={"path": "/dashboard", "page_title": "Dashboard"},
            timeout=15,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("ok") is True
        assert isinstance(body.get("ts"), str) and body["ts"]

    def test_heartbeat_is_idempotent_no_dupes(self, admin_headers, admin_token):
        admin_user_id = admin_token[1]["id"]
        # Two heartbeats from same admin
        for _ in range(2):
            r = requests.post(
                f"{API}/presence/heartbeat",
                headers=admin_headers,
                json={"path": "/members", "page_title": "Members"},
                timeout=15,
            )
            assert r.status_code == 200

        r = requests.get(f"{API}/presence/online", headers=admin_headers, timeout=15)
        assert r.status_code == 200, r.text
        body = r.json()
        users = body.get("users", [])
        admin_rows = [u for u in users if u.get("user_id") == admin_user_id]
        assert len(admin_rows) == 1, f"expected exactly one row for admin, got {len(admin_rows)}"

    def test_online_payload_shape(self, admin_headers, admin_token):
        # Ensure admin is fresh in presence
        requests.post(
            f"{API}/presence/heartbeat",
            headers=admin_headers,
            json={"path": "/aids", "page_title": "Aids"},
            timeout=15,
        )
        r = requests.get(f"{API}/presence/online", headers=admin_headers, timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert "users" in body and "count" in body
        assert isinstance(body["users"], list)
        assert body["count"] == len(body["users"])

        admin_user_id = admin_token[1]["id"]
        admin_row = next((u for u in body["users"] if u.get("user_id") == admin_user_id), None)
        assert admin_row, "admin not in /presence/online after heartbeat"
        # Required fields
        for key in ("user_id", "username", "display_name", "role", "path", "page_title", "last_seen"):
            assert key in admin_row, f"missing key '{key}' in presence row"
        # Forbidden / internal-only fields
        for forbidden in ("_id", "expires_at_dt", "last_seen_dt"):
            assert forbidden not in admin_row, f"presence row leaked internal field '{forbidden}'"
        # And it should reflect the latest heartbeat path/title
        assert admin_row["path"] == "/aids"
        assert admin_row["page_title"] == "Aids"

    def test_multi_user_online_count(self, admin_headers, mostafa_token, admin_token):
        # Both users beat
        mostafa_headers = {"Authorization": f"Bearer {mostafa_token[0]}"}
        r1 = requests.post(
            f"{API}/presence/heartbeat",
            headers=admin_headers,
            json={"path": "/dashboard", "page_title": "Dashboard"},
            timeout=15,
        )
        r2 = requests.post(
            f"{API}/presence/heartbeat",
            headers=mostafa_headers,
            json={"path": "/dashboard", "page_title": "Dashboard"},
            timeout=15,
        )
        assert r1.status_code == 200 and r2.status_code == 200

        r = requests.get(f"{API}/presence/online", headers=admin_headers, timeout=15)
        assert r.status_code == 200
        body = r.json()
        ids = {u.get("user_id") for u in body.get("users", [])}
        assert admin_token[1]["id"] in ids
        assert mostafa_token[1]["id"] in ids
        assert body.get("count", 0) >= 2

    def test_logout_removes_presence(self, admin_headers, mostafa_token, admin_token):
        mostafa_headers = {"Authorization": f"Bearer {mostafa_token[0]}"}
        # Ensure mostafa is currently visible
        requests.post(
            f"{API}/presence/heartbeat",
            headers=mostafa_headers,
            json={"path": "/x", "page_title": "X"},
            timeout=15,
        )

        r = requests.post(f"{API}/presence/logout", headers=mostafa_headers, timeout=15)
        assert r.status_code == 200, r.text
        assert r.json().get("ok") is True

        r = requests.get(f"{API}/presence/online", headers=admin_headers, timeout=15)
        assert r.status_code == 200
        ids = {u.get("user_id") for u in r.json().get("users", [])}
        assert mostafa_token[1]["id"] not in ids, "logged-out user still appears online"


# ─── Regressions: list aids + changes/state ─────────────────────────────────
class TestRegressions:
    def test_changes_state_shape(self, admin_headers):
        r = requests.get(f"{API}/changes/state", headers=admin_headers, timeout=15)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "counters" in body
        assert "updated_at" in body
        assert isinstance(body["counters"], dict)

    def test_aids_list_floor(self, admin_headers, department_id):
        r = requests.get(
            f"{API}/aids",
            params={"department_id": department_id},
            headers=admin_headers,
            timeout=20,
        )
        assert r.status_code == 200
        for record in r.json():
            from_month = (record.get("committee_dues") or {}).get("from_month", "")
            assert from_month >= "2025-01", f"aid {record.get('id')} has from_month {from_month}"

    def test_recalculate_bumps_aids_counter(self, admin_headers, sample_aid):
        # snapshot 1
        r1 = requests.get(f"{API}/changes/state", headers=admin_headers, timeout=15)
        assert r1.status_code == 200
        before = int((r1.json().get("counters") or {}).get("aids", 0))

        rc = requests.post(
            f"{API}/aids/{sample_aid['id']}/recalculate",
            headers=admin_headers,
            timeout=30,
        )
        assert rc.status_code == 200

        r2 = requests.get(f"{API}/changes/state", headers=admin_headers, timeout=15)
        assert r2.status_code == 200
        after = int((r2.json().get("counters") or {}).get("aids", 0))
        assert after == before + 1, f"counters.aids did not increment (before={before}, after={after})"
