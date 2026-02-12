# Context: TOEFL Listening Project

## پروژه چیست؟
میکروسرویس **TOEFL Listening Test & Practice**: آزمون/تمرین شنیداری با دو حالت **Exam Mode** و **Practice Mode**. طراحی UI مطابق اسکرین‌شات‌های فیگما در پوشه `Figma Screenshots/` و سند نیازمندی در `سند نیازمندی‌های نرم ‌افزار.pdf`. دیاگرام‌ها در `Diagrams/` (PlantUML).

## استک فنی
- **Backend:** Django + DRF، بدون لاگین (استفاده از کاربر مهمان `guest_listening`)، SQLite پیش‌فرض، آپلود صوت در `media/`.
- **Frontend:** React (Vite) + Tailwind CSS v4، بدون صفحه لاگین، پروکسی Vite به `http://127.0.0.1:8000` برای `/api` و `/media`.

## جریان فعلی اپ (User Flow)
1. **صفحه اصلی:** انتخاب حالت (Exam / Practice) با دو کارت.
2. **صفحه چک هدفون** (`/audio-setup?mode=...`): اسلایدر حجم، دکمه Continue، وضعیت System Ready / Microphone Not Required.
3. **صفحه راهنما** (`/directions?mode=...`): Listening Section Directions با چهار بلوک + TIMER RULE، دکمه‌های Back و Continue.
4. **شروع خودکار اولین تست:** با Continue از Directions به `/listening?testId=<اولین تست>&mode=...` می‌رود (بدون انتخاب دستی REAL 1 / REAL 2).
5. **فاز پلیر** (صفحه لکچر): فقط پلیر صدا (بدون ترنسکریپت روی صفحه). بالای صفحه سه دکمه **Review، Transcript، Settings** که هر کدام یک **پاپ‌آپ (Modal)** با انیمیشن باز می‌کنند. ترنسکریپت فقط داخل پاپ‌آپ Transcript نمایش داده می‌شود. با اتمام پخش صدا یا زدن **Continue** → رفتن به فاز سوالات.
6. **فاز سوالات:** هدر شبیه فیگما (Test Prep Pro، Quit، Back، آیکون‌های Review، Transcript، Notes، Question list، Settings، Audio، آواتار). زیر آن سوال چندگزینه‌ای، pagination (۱–۵)، دکمه‌های Continue / Finish.
7. **صفحه نتیجه:** Test Results Review با نمره و ساب‌اسکورها.

## مسیرهای مهم در کد
- **Backend:** `backend/config/settings.py`, `backend/listening/` (models, views, urls, serializers, services, admin). APIها: `GET /api/tests/`, `POST /api/sessions/start/`, `POST /api/sessions/<id>/answers/`, `POST /api/sessions/<id>/finish/`, `GET /api/sessions/<id>/score-report/`, `POST /api/sessions/<id>/events/`.
- **Frontend:** `frontend/src/App.jsx` (روت‌ها)، `frontend/src/pages/` (ModeSelect, AudioSetupPage, DirectionsPage, TestSelect, ListeningPage)، `frontend/src/components/` (AudioPlayer, QuestionCard, ScoreReportView, Transcript, PageHeader, Modal).
- **داده نمونه:** `python manage.py load_sample_data` (یا `--clear` برای جایگزینی). حدود ۵ تست، ۶ آیتم، ۱۰ سوال با ترنسکریپت انگلیسی.

## کارهای انجام‌شده در این چت
- راه‌اندازی Django (مدل‌ها، DRF، بدون اجباری بودن لاگین؛ کاربر مهمان برای درخواست‌های بدون توکن).
- پیاده‌سازی APIهای session، پاسخ، نمره، رویداد ضد تقلب (focus_loss, replay).
- راه‌اندازی React + Tailwind و پروکسی؛ حذف صفحه لاگین و اصلاح CORS/پروکسی برای رفع «Failed to fetch».
- طراحی مطابق فیگما: پالت رنگ (زرد برای دکمه‌ها، آبی برای انتخاب)، صفحه انتخاب حالت با کارت‌های Exam/Practice، صفحه چک هدفون، صفحه Directions.
- اضافه کردن جریان: بعد از Directions مستقیم به اولین تست (بدون صفحه انتخاب REAL 1/2).
- تفکیک فاز پلیر و فاز سوالات در ListeningPage؛ ترنسکریپت فقط با دکمه Transcript در پاپ‌آپ؛ پاپ‌آپ‌های Review، Transcript، Settings با Modal و انیمیشن؛ بعد از اتمام لکچر یا Continue رفتن به صفحه سوالات با هدر کامل (Quit, Back, آیکون‌ها).
- دستور `load_sample_data` برای پر کردن دیتابیس با داده نمونه.
- راهنمای گیت (خروج از اکانت قبلی با `cmdkey /delete:git:https://github.com`)، و یک کامیت با پیام مربوط به UI و sample data.

## خطاها و راه‌حل‌ها
- **ModuleNotFoundError: django:** نصب وابستگی‌ها در venv با `pip install -r requirements.txt` (و حذف django-storages/boto3 از requirements به‌خاطر ناسازگاری).
- **Failed to fetch:** استفاده از پروکسی Vite به بک‌اند و درخواست به `/api` از همان origin؛ اطمینان از روشن بودن بک‌اند قبل از فرانت.
- **Tailwind v4 PostCSS:** استفاده از `@tailwindcss/postcss` و `@import "tailwindcss"` در CSS.
- **git add failed (backend/ no commit):** حذف `backend/.git` (ریپوی تو در تو) تا فقط یک ریپو در روت پروژه باشد.
- **403 روی push:** پاک کردن credential گیت‌هاب با `cmdkey /delete:git:https://github.com` و ورود با اکانت/توکن صحیح.

## طراحی و مرجع
- فیگما: اسکرین‌شات‌ها در `Figma Screenshots/` (هر تصویر دو صفحه). لینک طراحی: `https://www.figma.com/design/Rdhjj0chLF6YbtOIMSd7EA/Listening_Figma`.
- رنگ‌ها و متغیرها در `frontend/src/index.css` با `@theme` (accent زرد، primary آبی، selected آبی روشن، و غیره).

## کارهایی که می‌توان در ادامه انجام داد
- تکمیل محتوای پاپ‌آپ **Review** (مثلاً لیست سوالات/پاسخ‌ها) و **Settings** (مثلاً حجم، سرعت پخش).
- پنل ادمین فرانت (مطابق فیگماهای ادمین) در صورت نیاز.
- پشتیبانی از چند آیتم/چند لکچر در یک تست و تعویض خودکار به آیتم بعدی بعد از اتمام سوالات یک آیتم.
- اتصال واقعی اسلایدر حجم در صفحه Audio Setup به سیستم/پلیر.

اگر چت جدید با این فایل شروع شود، ادامه کار باید با توجه به همین جریان، ساختار فایل‌ها و طراحی فیگما باشد.
