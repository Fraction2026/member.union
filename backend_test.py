#!/usr/bin/env python3
"""
Backend API Testing Script for Departments Endpoint
Tests POST /api/departments with various validation scenarios
"""

import requests
import json
from typing import Dict, Any, Optional

# Read backend URL from frontend/.env
BACKEND_URL = "https://union-dashboard.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(message: str):
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST: {message}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def login_as_admin() -> Optional[str]:
    """Login as admin and return the token"""
    print_test("تسجيل الدخول كـ Admin")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            },
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            user = data.get("user", {})
            print_success(f"تم تسجيل الدخول بنجاح - المستخدم: {user.get('username')} - الدور: {user.get('role')}")
            return token
        else:
            print_error(f"فشل تسجيل الدخول: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"خطأ في تسجيل الدخول: {str(e)}")
        return None

def test_empty_fields(token: str) -> bool:
    """Test 1: Try to add department with empty fields"""
    print_test("اختبار 1: إضافة إدارة بحقول فارغة")
    
    try:
        response = requests.post(
            f"{API_BASE}/departments",
            json={
                "name": "",
                "code": "",
                "description": ""
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text}")
        
        if response.status_code == 422:
            data = response.json()
            detail = data.get("detail", "")
            
            if detail == "اسم الإدارة مطلوب":
                print_success(f"الرسالة صحيحة: '{detail}'")
                return True
            else:
                print_error(f"الرسالة غير صحيحة. المتوقع: 'اسم الإدارة مطلوب', الفعلي: '{detail}'")
                return False
        else:
            print_error(f"كود الحالة غير متوقع. المتوقع: 422, الفعلي: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"خطأ في الاختبار: {str(e)}")
        return False

def test_name_only(token: str) -> bool:
    """Test 2: Try to add department with name only"""
    print_test("اختبار 2: إضافة إدارة مع اسم فقط")
    
    try:
        response = requests.post(
            f"{API_BASE}/departments",
            json={
                "name": "test",
                "code": "",
                "description": ""
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text}")
        
        if response.status_code == 422:
            data = response.json()
            detail = data.get("detail", "")
            
            if detail == "الكود المختصر مطلوب":
                print_success(f"الرسالة صحيحة: '{detail}'")
                return True
            else:
                print_error(f"الرسالة غير صحيحة. المتوقع: 'الكود المختصر مطلوب', الفعلي: '{detail}'")
                return False
        else:
            print_error(f"كود الحالة غير متوقع. المتوقع: 422, الفعلي: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"خطأ في الاختبار: {str(e)}")
        return False

def test_name_and_code_only(token: str) -> bool:
    """Test 3: Try to add department with name and code only"""
    print_test("اختبار 3: إضافة إدارة مع اسم وكود فقط")
    
    try:
        response = requests.post(
            f"{API_BASE}/departments",
            json={
                "name": "test",
                "code": "TST",
                "description": ""
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text}")
        
        if response.status_code == 422:
            data = response.json()
            detail = data.get("detail", "")
            
            if detail == "وصف الإدارة مطلوب":
                print_success(f"الرسالة صحيحة: '{detail}'")
                return True
            else:
                print_error(f"الرسالة غير صحيحة. المتوقع: 'وصف الإدارة مطلوب', الفعلي: '{detail}'")
                return False
        else:
            print_error(f"كود الحالة غير متوقع. المتوقع: 422, الفعلي: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"خطأ في الاختبار: {str(e)}")
        return False

def test_complete_department(token: str) -> bool:
    """Test 4: Add complete department"""
    print_test("اختبار 4: إضافة إدارة كاملة")
    
    try:
        response = requests.post(
            f"{API_BASE}/departments",
            json={
                "name": "test",
                "code": "TST",
                "description": "test desc"
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify the response contains the expected fields
            if (data.get("name") == "test" and 
                data.get("code") == "TST" and 
                data.get("description") == "test desc"):
                print_success("تم إضافة الإدارة بنجاح")
                print_info(f"ID: {data.get('id')}")
                print_info(f"Name: {data.get('name')}")
                print_info(f"Code: {data.get('code')}")
                print_info(f"Description: {data.get('description')}")
                return True
            else:
                print_error("البيانات المرجعة غير صحيحة")
                return False
        else:
            print_error(f"فشل إضافة الإدارة. كود الحالة: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"خطأ في الاختبار: {str(e)}")
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}اختبار نقطة النهاية: POST /api/departments{Colors.RESET}")
    print(f"{Colors.BLUE}Backend URL: {BACKEND_URL}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    # Step 1: Login as admin
    token = login_as_admin()
    if not token:
        print_error("\nفشل تسجيل الدخول. إيقاف الاختبارات.")
        return
    
    # Run all tests
    results = []
    
    results.append(("اختبار الحقول الفارغة", test_empty_fields(token)))
    results.append(("اختبار الاسم فقط", test_name_only(token)))
    results.append(("اختبار الاسم والكود فقط", test_name_and_code_only(token)))
    results.append(("اختبار الإدارة الكاملة", test_complete_department(token)))
    
    # Print summary
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}ملخص النتائج{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: نجح")
        else:
            print_error(f"{test_name}: فشل")
    
    print(f"\n{Colors.BLUE}النتيجة النهائية: {passed}/{total} اختبارات نجحت{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}جميع الاختبارات نجحت! ✓{Colors.RESET}\n")
    else:
        print(f"{Colors.RED}بعض الاختبارات فشلت! ✗{Colors.RESET}\n")

if __name__ == "__main__":
    main()
