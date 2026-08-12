# رحلاتي الذكية — منصة سفر وطيران ذكية

منصة ويب متكاملة للبحث عن رحلات الطيران ومقارنتها، مع مساعد سفر يعمل
بالذكاء الاصطناعي لتخطيط الرحلة بالكامل (الأماكن السياحية، الجدول
اليومي، الميزانية التقديرية).

> **ملاحظة مهمة**: جميع بيانات الرحلات المعروضة حاليًا هي بيانات
> **تجريبية (Mock Data)** يتم توليدها داخل الـ Backend، وليست بيانات
> حجز حقيقية. النظام مصمم بحيث يمكن استبدال مزود البيانات التجريبي
> بمزود حقيقي (API لشركة طيران أو خدمة تجميع رحلات) دون إعادة بناء
> المشروع.

---

## 1. البنية التقنية

```
travel-ai/
├── app.py                  # نقطة تشغيل Flask + تسجيل الصفحات والـ Blueprints
├── config.py                # إعدادات المشروع (تُقرأ من متغيرات البيئة)
├── extensions.py             # SQLAlchemy instance
├── models.py                 # جداول قاعدة البيانات
├── requirements.txt
├── Procfile                  # للتوافقية (Heroku-style) — Render يتطلب ضبط Start Command يدويًا في لوحته
├── runtime.txt                # للتوافقية مع منصات أخرى تقرأ هذا الملف (Heroku)
├── .python-version             # الطريقة التي يعتمدها Render فعليًا لتحديد إصدار Python
├── .gitignore
├── .env.example               # نموذج متغيرات البيئة
├── providers/                 # مزودو بيانات الرحلات (Modular)
│   ├── base.py                 # الواجهة المجردة FlightProvider
│   ├── mock_provider.py         # مزود تجريبي (Mock)
│   └── registry.py              # سجل المزودين المفعّلين
├── services/
│   ├── ai_service.py            # الواجهة الموحدة لخدمة الذكاء الاصطناعي
│   ├── ai_providers/
│   │   ├── base.py                # الواجهة المجردة AIProvider
│   │   ├── mock_ai_provider.py      # مزود ذكاء اصطناعي تجريبي (Rule-Based)
│   │   └── anthropic_provider.py     # مزود حقيقي (يعمل فقط عند ضبط API Key)
│   └── budget_service.py          # حساب الميزانية التقديرية
├── routes/                    # REST API endpoints (Flask Blueprints)
│   ├── health.py, flights.py, ai.py, budget.py,
│   └── destinations.py, auth.py, favorites.py, admin.py
├── data/                      # بيانات ثابتة أولية (مطارات، وجهات)
├── templates/                 # صفحات الواجهة الأمامية (Jinja2 + RTL عربي)
└── static/                    # CSS و JS
```

### فلسفة التصميم Backend → Provider Adapter

```
Frontend  →  Backend REST API  →  Flight/AI Provider Adapter  →  Provider حقيقي (لاحقًا)
```

- لا يوجد أي مفتاح API داخل الواجهة الأمامية أو الكود المصدري إطلاقًا.
- لإضافة شركة طيران أو مزود رحلات حقيقي: أضف ملفًا جديدًا في
  `providers/` يطبّق `FlightProvider` وسجّله في `providers/registry.py`.
- لتغيير مزود الذكاء الاصطناعي: أضف ملفًا جديدًا في
  `services/ai_providers/` يطبّق `AIProvider`، ثم فعّله عبر متغير البيئة
  `AI_PROVIDER`. إن لم يوجد مفتاح، يعمل النظام تلقائيًا بوضع تجريبي
  (`MockAIProvider`) بدون أي تعطل.

---

## 2. التشغيل محليًا

### المتطلبات
- Python 3.11+

### خطوات التشغيل

```bash
cd travel-ai
python -m venv venv
source venv/bin/activate        # على ويندوز: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# عدّل .env إذا أردت (اختياري - المشروع يعمل بدون أي تعديل)

python app.py
```

سيعمل المشروع على: `http://localhost:5000`

قاعدة البيانات الافتراضية SQLite ستُنشأ تلقائيًا في `instance/travel.db`
مع بيانات أولية (شركات طيران، وجهات، وحساب إداري تجريبي).

**حساب الإدارة الافتراضي (للتجربة فقط - غيّره فورًا في الإنتاج):**
- البريد: `admin@travel-ai.local`
- كلمة المرور: `ChangeMe123!`

---

## 3. النشر على Render

1. ادفع المشروع إلى مستودع GitHub — **عبر أوامر git من الطرفية وليس
   بالسحب والإفلات على واجهة GitHub الويب**، لتجنّب مشكلة فقدان مجلدات
   فرعية (راجع القسم 3.1 أدناه — هذا هو سبب خطأ `ModuleNotFoundError:
   No module named 'routes'` الشائع).
2. أنشئ **Web Service** جديد على [Render](https://render.com) واربطه بالمستودع.
3. إعدادات البناء — **أدخلها يدويًا في لوحة Render، فـ Render لا يقرأ
   Procfile تلقائيًا في بيئة Python الأصلية (هذا سلوك Heroku وليس
   Render)**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
     (ملف `Procfile` موجود في الجذر للتوافقية فقط ولا يتعارض مع هذا الحقل،
     لكن الحقل الفعلي في لوحة Render هو ما يُنفَّذ)
   - **Python Version**: ملف `.python-version` في جذر المشروع يحدد
     `3.11.9`. لضمان أن Render يلتزم به فعليًا (فـ Render الحالي لا
     يدعم `runtime.txt` كطريقة رسمية، ويستخدم افتراضيًا أحدث إصدار
     Python المتاح لديه إن لم يجد `.python-version` أو `PYTHON_VERSION`)،
     أضف أيضًا متغير بيئة `PYTHON_VERSION=3.11.9` يدويًا من تبويب
     Environment في لوحة Render — هذا له الأولوية القصوى ويضمن عدم
     استخدام إصدار غير متوقع.
4. أضف متغيرات البيئة من `.env.example` في لوحة Render (Environment):
   - `FLASK_SECRET_KEY` (قيمة عشوائية قوية)
   - `PYTHON_VERSION=3.11.9` (كما في الخطوة أعلاه)
   - `DATABASE_URL` (اختياري - أنشئ PostgreSQL من Render واربطه هنا، وإلا سيُستخدم SQLite محليًا داخل الحاوية)
   - `AI_PROVIDER`, `ANTHROPIC_API_KEY` (اختياري)
5. اضغط Deploy — المشروع سيعمل مباشرة دون أي تعديل إضافي.

> ملاحظة: تخزين SQLite داخل حاوية Render **غير دائم** بين عمليات
> إعادة النشر. للإنتاج الفعلي، اربط قاعدة بيانات PostgreSQL من Render
> عبر `DATABASE_URL`.

### 3.1 تحقق قبل الرفع: تأكد أن كل مجلدات Python وصلت إلى GitHub

هذا هو سبب خطأ `ModuleNotFoundError: No module named 'routes'` الشائع:
عند رفع المشروع يدويًا (سحب وإفلات على واجهة GitHub، أو أدوات مزامنة
معينة)، قد يتم تجاهل مجلدات كاملة أو ملفات صفرية الحجم مثل
`__init__.py`، فتختفي حزم بايثون بالكامل من المستودع الفعلي حتى لو
كانت موجودة عندك محليًا.

قبل كل `git push`، شغّل هذا الأمر من داخل مجلد المشروع للتأكد أن جميع
الملفات التالية مُتتبَّعة فعليًا بواسطة git:

```bash
git add -A
git status

# تحقق أن هذه المجلدات الأربعة موجودة ضمن القائمة:
git ls-files | grep -E "^(routes|providers|services|data)/"
```

يجب أن ترى في المخرجات كل ملفات `routes/*.py`، `providers/*.py`،
`services/*.py`، `services/ai_providers/*.py`، و`data/*.py` — بما في
ذلك ملفات `__init__.py`. إذا كان أي منها مفقودًا، نفّذ:

```bash
git add routes providers services data
git commit -m "fix: ensure all backend packages are tracked"
git push
```

ثم أعد النشر (Manual Deploy) على Render.

---

## 4. أهم نقاط الـ REST API

| Method | Endpoint | الوصف |
|---|---|---|
| GET | `/api/health` | فحص حالة السيرفر |
| GET | `/api/airports?q=` | إكمال تلقائي للمطارات/المدن |
| POST | `/api/flights/search` | بحث عن رحلات (يدعم `sort_by`) |
| POST | `/api/flights/details` | تفاصيل رحلة واحدة |
| POST | `/api/flights/compare` | مقارنة ذكية بين رحلتين |
| POST | `/api/ai/popular-places` | أشهر الأماكن في وجهة معينة |
| POST | `/api/ai/plan-trip` | إنشاء جدول رحلة يومي (مدخلات منظمة) |
| POST | `/api/ai/plan-full-trip` | تخطيط رحلة كاملة من نص حر |
| POST | `/api/budget/estimate` | تقدير ميزانية الرحلة |
| GET | `/api/destinations` | قائمة الوجهات |
| POST | `/api/auth/register` `/login` `/logout` | المصادقة |
| GET/POST/DELETE | `/api/favorites` | المفضلة |
| GET | `/api/admin/*` | لوحة الإدارة (تتطلب صلاحية admin) |

---

## 5. الحالة الحالية للمزودين

- **الرحلات**: `MockFlightProvider` فقط حاليًا (بيانات تجريبية واضحة
  المعالم عبر `is_mock: true`). لا يوجد افتراض بوجود API عام لشركات
  الطيران السعودية.
- **الذكاء الاصطناعي**: `MockAIProvider` (قائم على قواعد، يعمل دائمًا
  بدون مفتاح). عند ضبط `AI_PROVIDER=anthropic` و`ANTHROPIC_API_KEY`
  في البيئة، يتم استخدام `AnthropicAIProvider` تلقائيًا مع رجوع آمن
  (Fallback) للمزود التجريبي عند أي خطأ.
- **الفنادق / تأجير السيارات / المطاعم**: جدول `Hotel` جاهز في قاعدة
  البيانات كنقطة بداية، ولم تُربط بواجهة بعد — جاهزة للتوسعة المستقبلية.

---

## 6. الاختبار السريع بعد التشغيل

```bash
curl http://localhost:5000/api/health

curl -X POST http://localhost:5000/api/flights/search \
  -H "Content-Type: application/json" \
  -d '{"origin":"RUH","destination":"IST","depart_date":"2026-09-01","passengers":1,"cabin_class":"economy"}'

curl -X POST http://localhost:5000/api/ai/plan-trip \
  -H "Content-Type: application/json" \
  -d '{"destination":"إسطنبول","days":4,"budget":4000,"trip_type":"عائلية","interests":"تسوق ومطاعم"}'
```
