"""Verification of the simplified member-duplicate rules.

Final rule: a record is rejected as duplicate when EITHER membership_number
OR national_id is already used by another member in the SAME
(department_id + governorate + union_committee). Anything else is allowed.
"""
import asyncio, os, sys
sys.path.insert(0, "/app/backend")
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ.get("DB_NAME", "test_database")


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    from server import _find_member_duplicate, _duplicate_reason

    test_dept = "TEST_DEDUP_DEPT_X"
    await db.members.delete_many({"department_id": test_dept})

    seed = {
        "id": "seed-1",
        "department_id": test_dept,
        "name": "أحمد محمد علي حسن",
        "national_id": "29001011234567",
        "membership_number": "1001",
        "governorate": "الإسكندرية",
        "union_committee": "لجنة الميناء",
    }
    await db.members.insert_one({**seed})

    cases = [
        # (label, candidate, expect_block)
        ("1. نفس رقم العضوية + لجنة مختلفة، محافظة مختلفة",
         {"department_id": test_dept, "name": "أ", "national_id": "11111111111111",
          "membership_number": "1001", "governorate": "أسوان", "union_committee": "لجنة أخرى"}, False),
        ("2. نفس رقم العضوية + نفس اللجنة + نفس المحافظة",
         {"department_id": test_dept, "name": "ب", "national_id": "22222222222222",
          "membership_number": "1001", "governorate": "الإسكندرية", "union_committee": "لجنة الميناء"}, True),
        ("3. نفس رقم العضوية + نفس اللجنة + محافظة مختلفة → مسموح (لأن المحافظة مختلفة)",
         {"department_id": test_dept, "name": "ج", "national_id": "33333333333333",
          "membership_number": "1001", "governorate": "أسوان", "union_committee": "لجنة الميناء"}, False),
        ("4. نفس الرقم القومي + لجنة مختلفة",
         {"department_id": test_dept, "name": "د", "national_id": "29001011234567",
          "membership_number": "9999", "governorate": "الإسكندرية", "union_committee": "لجنة أخرى"}, False),
        ("5. نفس الرقم القومي + نفس اللجنة + نفس المحافظة",
         {"department_id": test_dept, "name": "هـ", "national_id": "29001011234567",
          "membership_number": "9998", "governorate": "الإسكندرية", "union_committee": "لجنة الميناء"}, True),
        ("6. نفس الاسم الرباعي تماماً + بيانات أخرى مختلفة",
         {"department_id": test_dept, "name": "أحمد محمد علي حسن", "national_id": "44444444444444",
          "membership_number": "9997", "governorate": "أسوان", "union_committee": "لجنة جديدة"}, False),
        ("7. كل البيانات مختلفة",
         {"department_id": test_dept, "name": "ز", "national_id": "55555555555555",
          "membership_number": "9996", "governorate": "أسوان", "union_committee": "لجنة جديدة"}, False),
    ]

    failures = 0
    for label, cand, expect in cases:
        dup = await _find_member_duplicate(cand)
        actual = bool(dup)
        ok = actual == expect
        flag = "✅" if ok else "❌"
        reason = _duplicate_reason(dup, cand) if dup else "—"
        print(f"{flag} {label}\n     expected_block={expect}, actual_block={actual}, reason={reason}")
        if not ok:
            failures += 1

    await db.members.delete_many({"department_id": test_dept})
    print(f"\n{'='*60}\nTotal: {len(cases) - failures}/{len(cases)} passed")
    if failures:
        sys.exit(1)


asyncio.run(main())
