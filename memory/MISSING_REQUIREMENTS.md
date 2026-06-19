# الاحتياجات البرمجية الناقصة - نظام member.union

> **ملاحظة مهمة**: هذه القائمة لا تتضمن أي تعديلات على العمليات الحسابية أو المبالغ المالية

---

## 🔴 أولوية قصوى (Critical Priority)

### 1. الأمان (Security)

#### أ. استبدال نظام تشفير كلمات المرور
**الوضع الحالي**: SHA256 (ضعيف وسريع الاختراق)  
**المطلوب**: استخدام bcrypt أو argon2

```python
# استبدال هذا الكود:
def hash_password(password: str, salt: Optional[str] = None):
    digest = hashlib.sha256(f"{password_salt}:{password}".encode("utf-8")).hexdigest()
    
# بهذا:
import bcrypt
def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

**الفائدة**: حماية كلمات المرور من هجمات Rainbow Tables و Brute Force

---

#### ب. إضافة Rate Limiting
**المطلوب**: الحد من عدد الطلبات من نفس IP

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@api_router.post("/auth/login")
@limiter.limit("5/minute")  # 5 محاولات فقط كل دقيقة
async def login(...):
    ...
```

**الفائدة**: حماية من هجمات Brute Force و DDoS

---

#### ج. تقييد CORS
**الوضع الحالي**:
```python
CORS_ORIGINS="*"  # يسمح لأي موقع!
```

**المطلوب**:
```python
# في .env
CORS_ORIGINS="https://union-dashboard.preview.emergentagent.com,https://yourdomain.com"
```

**الفائدة**: منع المواقع الخبيثة من الوصول للـ APIs

---

#### د. إضافة Input Sanitization
**المطلوب**: تنظيف جميع المدخلات من HTML/JavaScript الخبيث

```python
import bleach

def sanitize_input(text: str) -> str:
    return bleach.clean(text, tags=[], strip=True)
```

**الفائدة**: حماية من هجمات XSS

---

#### هـ. إضافة CSRF Protection
**المطلوب**: إضافة CSRF tokens لجميع النماذج

```python
from starlette_csrf import CSRFMiddleware
app.add_middleware(CSRFMiddleware, secret="your-secret-key")
```

**الفائدة**: حماية من هجمات Cross-Site Request Forgery

---

#### و. إضافة Security Headers
**المطلوب**:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.emergentagent.com"])
# app.add_middleware(HTTPSRedirectMiddleware)  # في الإنتاج فقط
```

**الفائدة**: حماية من هجمات Man-in-the-Middle

---

#### ز. إضافة Audit Logging
**المطلوب**: تسجيل جميع العمليات الحساسة

```python
async def log_audit(user_id: str, action: str, resource: str, details: dict):
    await db.audit_logs.insert_one({
        "user_id": user_id,
        "action": action,  # "create", "update", "delete"
        "resource": resource,  # "member", "subscription", etc
        "details": details,
        "timestamp": now_iso(),
        "ip_address": request.client.host
    })
```

**الفائدة**: تتبع جميع التغييرات ومعرفة من فعل ماذا ومتى

---

### 2. الاختبار (Testing)

#### أ. إضافة Unit Tests
**المطلوب**: اختبارات للـ Functions الأساسية

```python
# tests/test_auth.py
import pytest
from backend.server import hash_password, verify_password

def test_password_hashing():
    password = "test123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) == True
    assert verify_password("wrong", hashed) == False
```

**الفائدة**: التأكد من أن الكود يعمل بشكل صحيح بعد أي تعديل

---

#### ب. إضافة Integration Tests
**المطلوب**: اختبار APIs بشكل كامل

```python
# tests/test_api_members.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_member():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/members", json={...})
        assert response.status_code == 200
```

---

#### ج. إضافة E2E Tests للـ Frontend
**المطلوب**: اختبار رحلة المستخدم الكاملة

```javascript
// tests/e2e/login.spec.js
test('should login successfully', async ({ page }) => {
  await page.goto('/');
  await page.fill('input[type="text"]', 'admin');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/departments');
});
```

---

## 🟠 أولوية عالية (High Priority)

### 3. تحسين تجربة المستخدم (UX)

#### أ. رسائل خطأ واضحة بالعربية
**الوضع الحالي**:
```json
{"detail":[{"type":"missing","loc":["query","department_id"],"msg":"Field required"}]}
```

**المطلوب**:
```python
class ArabicErrorHandler:
    @staticmethod
    def format_error(exc):
        if exc.type == "missing":
            field_name = FIELD_NAMES_AR.get(exc.loc[-1], exc.loc[-1])
            return f"الحقل '{field_name}' مطلوب"
        elif exc.type == "value_error":
            return f"القيمة المدخلة غير صحيحة"
```

**الفائدة**: المستخدم يفهم المشكلة بسرعة

---

#### ب. إضافة Loading States
**المطلوب**: في Frontend

```javascript
const [loading, setLoading] = useState(false);

const handleSubmit = async () => {
  setLoading(true);
  try {
    await api.post('/members', data);
  } finally {
    setLoading(false);
  }
};

return (
  <Button disabled={loading}>
    {loading && <Loader2 className="animate-spin" />}
    حفظ
  </Button>
);
```

**الفائدة**: المستخدم يعرف أن العملية جارية

---

#### ج. إضافة Toast Notifications محسّنة
**المطلوب**:
```javascript
import { toast } from 'sonner';

// بدلاً من:
alert('تم الحفظ');

// استخدم:
toast.success('تم حفظ البيانات بنجاح', {
  description: 'يمكنك الآن مشاهدة العضو في القائمة',
  action: {
    label: 'عرض',
    onClick: () => navigate(`/member/${id}`)
  }
});
```

**الفائدة**: تجربة مستخدم أفضل

---

#### د. إضافة Skeleton Loaders
**المطلوب**: بدلاً من شاشة بيضاء أثناء التحميل

```javascript
{loading ? (
  <div className="space-y-2">
    <Skeleton className="h-12 w-full" />
    <Skeleton className="h-12 w-full" />
    <Skeleton className="h-12 w-full" />
  </div>
) : (
  <MembersList />
)}
```

**الفائدة**: شعور بسرعة أكبر

---

### 4. إدارة البيانات (Data Management)

#### أ. Soft Delete بدلاً من Hard Delete
**الوضع الحالي**: عند الحذف، البيانات تُحذف نهائياً

**المطلوب**:
```python
# بدلاً من:
await db.members.delete_one({"id": member_id})

# استخدم:
await db.members.update_one(
    {"id": member_id},
    {"$set": {
        "deleted": True,
        "deleted_at": now_iso(),
        "deleted_by": user_id
    }}
)

# وفي الاستعلامات:
members = await db.members.find({"deleted": {"$ne": True}}).to_list()
```

**الفائدة**: إمكانية استرجاع البيانات المحذوفة

---

#### ب. Version History للسجلات
**المطلوب**: حفظ تاريخ التعديلات

```python
async def update_member_with_history(member_id: str, updates: dict, user_id: str):
    # حفظ النسخة القديمة
    old_member = await db.members.find_one({"id": member_id})
    await db.member_history.insert_one({
        "member_id": member_id,
        "version": old_member.get("version", 0),
        "data": old_member,
        "updated_by": user_id,
        "updated_at": now_iso()
    })
    
    # تحديث النسخة الجديدة
    updates["version"] = old_member.get("version", 0) + 1
    await db.members.update_one({"id": member_id}, {"$set": updates})
```

**الفائدة**: معرفة من غيّر ماذا ومتى

---

#### ج. Data Validation Rules أقوى
**المطلوب**:
```python
from pydantic import validator

class MemberIn(BaseModel):
    national_id: str
    
    @validator('national_id')
    def validate_national_id(cls, v):
        # التحقق من الرقم القومي المصري (14 رقم)
        if not v.isdigit() or len(v) != 14:
            raise ValueError('الرقم القومي يجب أن يكون 14 رقماً')
        return v
    
    phone: str
    
    @validator('phone')
    def validate_phone(cls, v):
        # التحقق من رقم الهاتف المصري
        if not v.startswith('01') or len(v) != 11:
            raise ValueError('رقم الهاتف غير صحيح')
        return v
```

**الفائدة**: منع البيانات الخاطئة من الدخول

---

#### د. Duplicate Detection تلقائي
**المطلوب**: قبل حفظ عضو جديد

```python
async def check_duplicate_member(national_id: str, department_id: str):
    existing = await db.members.find_one({
        "national_id": national_id,
        "department_id": department_id,
        "deleted": {"$ne": True}
    })
    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "duplicate",
                "message": f"العضو موجود بالفعل: {existing['name']}",
                "existing_member": existing
            }
        )
```

**الفائدة**: منع التكرار

---

## 🟡 أولوية متوسطة (Medium Priority)

### 5. الأداء (Performance)

#### أ. إضافة Redis للـ Caching
**المطلوب**:
```python
import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

redis_client = redis.from_url("redis://localhost")
FastAPICache.init(RedisBackend(redis_client), prefix="member-union-cache")

@api_router.get("/departments")
@cache(expire=300)  # 5 دقائق
async def get_departments():
    return await db.departments.find({}).to_list()
```

**الفائدة**: تسريع الاستعلامات المتكررة

---

#### ب. Database Connection Pooling
**المطلوب**:
```python
client = AsyncIOMotorClient(
    mongo_url,
    maxPoolSize=50,  # عدد الاتصالات المسموح بها
    minPoolSize=10,
    connectTimeoutMS=5000,
    serverSelectionTimeoutMS=5000
)
```

**الفائدة**: أداء أفضل مع عدد مستخدمين كبير

---

#### ج. Pagination Enhancement
**المطلوب**: في جميع الاستعلامات الكبيرة

```python
@api_router.get("/members")
async def get_members(
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "created_at",
    sort_order: int = -1
):
    skip = (page - 1) * page_size
    total = await db.members.count_documents({})
    members = await db.members.find({}) \
        .sort(sort_by, sort_order) \
        .skip(skip) \
        .limit(page_size) \
        .to_list()
    
    return {
        "data": members,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }
```

**الفائدة**: تحميل أسرع

---

### 6. المراقبة والتتبع (Monitoring)

#### أ. إضافة Error Tracking (Sentry)
**المطلوب**:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

**الفائدة**: معرفة الأخطاء فوراً

---

#### ب. إضافة Application Performance Monitoring
**المطلوب**:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

**الفائدة**: معرفة أداء كل API

---

#### ج. إضافة Health Check شامل
**المطلوب**:
```python
@api_router.get("/health/full")
async def health_check_full():
    checks = {
        "api": "ok",
        "database": await check_db_connection(),
        "redis": await check_redis_connection(),
        "disk_space": await check_disk_space(),
        "memory": await check_memory_usage(),
    }
    
    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ok" if all_ok else "degraded",
        "checks": checks,
        "timestamp": now_iso()
    }
```

**الفائدة**: معرفة صحة النظام

---

### 7. الميزات الإضافية

#### أ. Dark Mode
**المطلوب**: في Frontend

```javascript
import { ThemeProvider } from 'next-themes';

function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="light">
      <YourApp />
    </ThemeProvider>
  );
}
```

**الفائدة**: راحة للعين في الليل

---

#### ب. Bulk Operations
**المطلوب**: حذف/تعديل عدة سجلات دفعة واحدة

```python
@api_router.delete("/members/bulk")
async def delete_members_bulk(
    ids: List[str] = Body(...),
    user: Dict = Depends(require_admin)
):
    result = await db.members.update_many(
        {"id": {"$in": ids}},
        {"$set": {
            "deleted": True,
            "deleted_at": now_iso(),
            "deleted_by": user["id"]
        }}
    )
    return {"deleted_count": result.modified_count}
```

**الفائدة**: توفير الوقت

---

#### ج. Advanced Search
**المطلوب**: بحث متقدم بعدة معايير

```python
@api_router.post("/members/search")
async def search_members(query: SearchQuery):
    filter_dict = {}
    
    if query.name:
        filter_dict["name"] = {"$regex": query.name, "$options": "i"}
    
    if query.governorate:
        filter_dict["governorate"] = query.governorate
    
    if query.status:
        filter_dict["status"] = {"$in": query.status}
    
    if query.date_from and query.date_to:
        filter_dict["created_at"] = {
            "$gte": query.date_from,
            "$lte": query.date_to
        }
    
    members = await db.members.find(filter_dict).to_list()
    return members
```

**الفائدة**: إيجاد البيانات بسرعة

---

#### د. Notifications System
**المطلوب**: إشعارات داخل التطبيق

```python
# Backend
async def create_notification(user_id: str, title: str, message: str, type: str):
    await db.notifications.insert_one({
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": type,  # "info", "success", "warning", "error"
        "read": False,
        "created_at": now_iso()
    })

# Frontend
const { data: notifications } = useSWR('/api/notifications', fetcher);
```

**الفائدة**: إخبار المستخدمين بالأحداث المهمة

---

## 🟢 أولوية منخفضة (Nice to Have)

### 8. تحسينات إضافية

#### أ. Email Notifications
**المطلوب**:
```python
from fastapi_mail import FastMail, MessageSchema

async def send_email(to: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[to],
        body=body,
        subtype="html"
    )
    await FastMail(email_conf).send_message(message)
```

---

#### ب. 2FA (Two-Factor Authentication)
**المطلوب**:
```python
import pyotp

def generate_2fa_secret():
    return pyotp.random_base32()

def verify_2fa_token(secret: str, token: str):
    totp = pyotp.TOTP(secret)
    return totp.verify(token)
```

---

#### ج. Advanced Charts & Reports
**المطلوب**: في Frontend باستخدام recharts

```javascript
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

<BarChart data={membersByMonth}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="month" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="count" fill="#0047AB" />
</BarChart>
```

---

#### د. Keyboard Shortcuts
**المطلوب**:
```javascript
import { useHotkeys } from 'react-hotkeys-hook';

useHotkeys('ctrl+n', () => openNewMemberDialog());
useHotkeys('ctrl+s', () => saveCurrentForm());
useHotkeys('ctrl+f', () => focusSearchInput());
```

---

## 📋 قائمة التحقق (Checklist)

### الأمان (Security)
- [ ] استبدال SHA256 بـ bcrypt
- [ ] إضافة Rate Limiting
- [ ] تقييد CORS
- [ ] إضافة Input Sanitization
- [ ] إضافة CSRF Protection
- [ ] إضافة Security Headers
- [ ] إضافة Audit Logging
- [ ] إضافة 2FA (اختياري)

### الاختبار (Testing)
- [ ] إضافة Unit Tests
- [ ] إضافة Integration Tests
- [ ] إضافة E2E Tests
- [ ] إضافة Load Tests
- [ ] إضافة CI/CD Pipeline

### تجربة المستخدم (UX)
- [ ] رسائل خطأ واضحة بالعربية
- [ ] Loading States
- [ ] Skeleton Loaders
- [ ] Toast Notifications محسّنة
- [ ] تحسين Mobile Experience
- [ ] إضافة Dark Mode
- [ ] إضافة Keyboard Shortcuts

### إدارة البيانات (Data)
- [ ] Soft Delete
- [ ] Version History
- [ ] Data Validation أقوى
- [ ] Duplicate Detection
- [ ] Bulk Operations

### الأداء (Performance)
- [ ] Redis Caching
- [ ] Database Connection Pooling
- [ ] Pagination Enhancement
- [ ] Index Optimization

### المراقبة (Monitoring)
- [ ] Error Tracking (Sentry)
- [ ] APM (Prometheus)
- [ ] Health Check شامل
- [ ] Structured Logging

### الميزات الإضافية
- [ ] Notifications System
- [ ] Advanced Search
- [ ] Email Notifications
- [ ] Advanced Charts
- [ ] Export PDF Reports

---

## 📊 تقدير الوقت لكل مجموعة

| المجموعة | الوقت التقديري |
|---------|----------------|
| الأمان (Security) | 3-5 أيام |
| الاختبار (Testing) | 5-7 أيام |
| تجربة المستخدم (UX) | 4-6 أيام |
| إدارة البيانات | 3-4 أيام |
| الأداء | 2-3 أيام |
| المراقبة | 2-3 أيام |
| الميزات الإضافية | 5-10 أيام |

**الإجمالي التقديري**: 24-38 يوم عمل (حوالي 5-8 أسابيع)

---

**تاريخ التقرير**: 19 يونيو 2026  
**ملاحظة**: هذه القائمة قابلة للتحديث بناءً على الأولويات والاحتياجات
