"""Tests for inheritance calculator (Islamic inheritance with فرض، رد، تعصيب)."""
import os
import sys
import pytest
import requests
from fractions import Fraction

# Allow direct import of calculator
sys.path.insert(0, "/app/backend")
from services.inheritance_calculator import calculate_inheritance  # noqa: E402

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/") or "http://localhost:8001"


# ---------- Direct function tests ----------
class TestInheritanceCalculatorDirect:
    """Test the calculate_inheritance function directly."""

    def _check_required_fields(self, b):
        for f in ["base_share_fraction", "base_share_arabic", "radd_fraction",
                  "final_share_fraction", "share_type", "amount", "name", "relation"]:
            assert f in b, f"Missing field: {f} in {b}"

    def test_wife_plus_4_daughters_radd(self):
        """زوجة + 4 بنات: زوجة 1/8 فرض، البنات 2/3 + رد"""
        bens = [{"name": "الزوجة", "relation": "زوجة"}] + \
               [{"name": f"بنت{i}", "relation": "ابنة"} for i in range(1, 5)]
        result = calculate_inheritance(24000, bens)
        rs = result["results"]
        assert len(rs) == 5
        for b in rs:
            self._check_required_fields(b)

        wife = next(r for r in rs if r["relation"] == "زوجة")
        assert wife["share_type"] == "فرض"
        assert wife["base_share_arabic"] == "ثمن"
        assert wife["radd_fraction"] == ""
        assert wife["base_share_fraction"] == "1/8"
        assert abs(wife["amount"] - 3000.0) < 0.01  # 24000/8

        daughters = [r for r in rs if r["relation"] == "ابنة"]
        assert len(daughters) == 4
        for d in daughters:
            assert d["share_type"] == "فرض + رد"
            assert d["base_share_arabic"] == "ثلثان"
            assert d["radd_fraction"] != ""  # has radd
        # Sum should equal total
        assert abs(sum(r["amount"] for r in rs) - 24000.0) < 0.5

    def test_husband_mother_daughter_radd(self):
        """زوج + أم + بنت: زوج 1/4، أم 1/6، بنت 1/2، الباقي رد على الأم والبنت"""
        bens = [
            {"name": "الزوج", "relation": "زوج"},
            {"name": "الأم", "relation": "أم"},
            {"name": "البنت", "relation": "ابنة"},
        ]
        result = calculate_inheritance(12000, bens)
        rs = result["results"]
        assert len(rs) == 3
        husband = next(r for r in rs if r["relation"] == "زوج")
        mother = next(r for r in rs if r["relation"] == "أم")
        daughter = next(r for r in rs if r["relation"] == "ابنة")

        # Husband: 1/4 farḍ, no radd
        assert husband["share_type"] == "فرض"
        assert husband["base_share_arabic"] == "ربع"
        assert husband["radd_fraction"] == ""
        # Mother and daughter get radd
        assert mother["share_type"] == "فرض + رد"
        assert mother["base_share_arabic"] == "سدس"
        assert mother["radd_fraction"] != ""
        assert daughter["share_type"] == "فرض + رد"
        assert daughter["base_share_arabic"] == "نصف"
        assert daughter["radd_fraction"] != ""

        # Mathematical correctness: total ≈ original
        total = sum(r["amount"] for r in rs)
        assert abs(total - 12000.0) < 0.5

    def test_wife_son_two_daughters_tasseeb(self):
        """زوجة + ابن + ابنتان: زوجة 1/8، الباقي تعصيباً (للذكر مثل حظ الأنثيين)"""
        bens = [
            {"name": "الزوجة", "relation": "زوجة"},
            {"name": "الابن", "relation": "ابن"},
            {"name": "بنت1", "relation": "ابنة"},
            {"name": "بنت2", "relation": "ابنة"},
        ]
        result = calculate_inheritance(32000, bens)
        rs = result["results"]
        assert len(rs) == 4

        wife = next(r for r in rs if r["relation"] == "زوجة")
        assert wife["share_type"] == "فرض"
        assert wife["base_share_arabic"] == "ثمن"
        assert abs(wife["amount"] - 4000.0) < 0.01  # 32000/8

        son = next(r for r in rs if r["relation"] == "ابن")
        daughters = [r for r in rs if r["relation"] == "ابنة"]
        assert son["share_type"] == "تعصيب"
        for d in daughters:
            assert d["share_type"] == "تعصيب"
            assert d["radd_fraction"] == ""

        # Son = 2 * each daughter
        assert abs(son["amount"] - 2 * daughters[0]["amount"]) < 0.5
        total = sum(r["amount"] for r in rs)
        assert abs(total - 32000.0) < 0.5


# ---------- API endpoint tests ----------
@pytest.fixture(scope="module")
def auth_token():
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"username": "admin", "password": "admin123"}, timeout=15)
    if r.status_code != 200:
        pytest.skip(f"Login failed: {r.status_code} {r.text}")
    return r.json().get("token") or r.json().get("access_token")


@pytest.fixture(scope="module")
def aid_id(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Find a department first
    d = requests.get(f"{BASE_URL}/api/departments", headers=headers, timeout=15)
    if d.status_code != 200 or not d.json():
        pytest.skip("No departments found")
    dept_id = d.json()[0]["id"]
    r = requests.get(f"{BASE_URL}/api/aids", params={"department_id": dept_id},
                     headers=headers, timeout=20)
    if r.status_code == 200:
        items = r.json() if isinstance(r.json(), list) else []
        if items:
            return items[0].get("id")
    pytest.skip("No aid available to test calculate-beneficiaries endpoint")


class TestCalculateBeneficiariesAPI:
    def test_endpoint_returns_new_fields(self, auth_token, aid_id):
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "total_amount": 24000,
            "beneficiaries": [
                {"name": "الزوجة", "relation": "زوجة"},
                {"name": "بنت1", "relation": "ابنة"},
                {"name": "بنت2", "relation": "ابنة"},
                {"name": "بنت3", "relation": "ابنة"},
                {"name": "بنت4", "relation": "ابنة"},
            ],
        }
        r = requests.post(f"{BASE_URL}/api/aids/{aid_id}/calculate-beneficiaries",
                          headers=headers, json=payload, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "results" in data
        for b in data["results"]:
            for f in ["base_share_fraction", "base_share_arabic", "radd_fraction",
                      "final_share_fraction", "share_type"]:
                assert f in b, f"Missing {f} in API response: {b}"
        # Daughters should have radd
        daughters = [r for r in data["results"] if r["relation"] == "ابنة"]
        assert all(d["share_type"] == "فرض + رد" for d in daughters)

    def test_endpoint_tasseeb_case(self, auth_token, aid_id):
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "total_amount": 32000,
            "beneficiaries": [
                {"name": "الزوجة", "relation": "زوجة"},
                {"name": "الابن", "relation": "ابن"},
                {"name": "بنت1", "relation": "ابنة"},
                {"name": "بنت2", "relation": "ابنة"},
            ],
        }
        r = requests.post(f"{BASE_URL}/api/aids/{aid_id}/calculate-beneficiaries",
                          headers=headers, json=payload, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        son = next(b for b in data["results"] if b["relation"] == "ابن")
        assert son["share_type"] == "تعصيب"

    def test_endpoint_invalid_total(self, auth_token, aid_id):
        headers = {"Authorization": f"Bearer {auth_token}"}
        r = requests.post(f"{BASE_URL}/api/aids/{aid_id}/calculate-beneficiaries",
                          headers=headers,
                          json={"total_amount": 0, "beneficiaries": [{"name": "x", "relation": "زوجة"}]},
                          timeout=15)
        assert r.status_code == 400
