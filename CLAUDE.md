# pharm_bot — CLAUDE.md

aiogram 3 (long polling) Telegram boti. Yagona vazifasi: sotuvchi (seller) **live location + video note**
yuboradi → bot buni backend'ga (`../pharmacy_backend`) `UserGeoLocation` sifatida saqlaydi va
barcha admin/superadmin'larga (matn + video + lokatsiya) yuboradi. Mini-app keyin shu geo'ga tayanib
tur planni "tasdiqlash"ga ruxsat beradi.

## Ishga tushirish

```bash
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env        # BOT_TOKEN majburiy; BACKEND_URL ixtiyoriy
python main.py
```

Tekshiruv: `python -m py_compile main.py bot/*.py bot/**/*.py`. Testlar yo'q.
Eslatma: `aiogram==3.22.0` Python 3.14 uchun wheel'lari yo'q — 3.11/3.12 ishlating.

## Tuzilma

```
main.py                 Bot/Dispatcher, MemoryStorage, logging, shutdown'da httpx client yopiladi
bot/config/env.py       BOT_TOKEN, BACKEND_URL (default prod), HTTP_TIMEOUT, BOT_API_SECRET; DB_* legacy (ixtiyoriy)
bot/services/api.py     Backend'ga yagona kirish: request_json() -> (status, body); tarmoq xatosi -> (0, None).
                        BOT_API_SECRET bo'lsa har so'rovga `X-Bot-Secret` header qo'shiladi.
bot/services/user.py    get_user_by_chat() (/users/profile/), get_all_admins()
bot/services/geo_location.py  create_geo_location() (POST /users/create_geo_location/)
bot/start_router.py     Handlerlar: /start, "📍 Joylashuv yuborish", location, video_note
bot/state.py            GeoVideoState: waiting_for_location -> waiting_for_video
bot/keyboard.py         Reply keyboard (bitta tugma)
bot/helpers.py, bot/config/database.py, bot/config/models.py — LEGACY: to'g'ridan-to'g'ri asyncpg
                        ulanish; hozir hech qayerda import qilinmaydi, SQL sxemasi Django modellariga
                        mos kelmaydi. Ishlatmang; xohlasangiz o'chirib tashlash mumkin.
```

## Oqim

1. `/start` → `GET /users/profile/?chat_id=` : yo'q → "web app orqali ro'yxatdan o'ting";
   `status != accepted` → "tasdiqlanmagan"; aks holda tugma.
2. Tugma → `waiting_for_location`. Faqat **live** location qabul qilinadi (`live_period` bor).
3. `waiting_for_video` → faqat `video_note`. `POST /users/create_geo_location/` 201 bo'lsa "saqlandi",
   aks holda xato xabari (backend 403 = user tasdiqlanmagan).
4. `GET /users/get_all_admins/` → har bir adminga `send_message` + `send_video_note` + `send_location`;
   bitta admin xato bersa (botni start qilmagan) qolganlarga davom etadi.

## Konventsiyalar / gotchalar

- Servislar **exception tashlamaydi**: muvaffaqiyatsiz bo'lsa `None`/`[]` qaytaradi; handler foydalanuvchiga
  xabar beradi. Yangi API chaqiruvlarini `bot/services/api.py::request_json` orqali yozing.
- Backend `chat_id` ni har so'rovda talab qiladi (query param yoki body). Backend'da
  `TELEGRAM_AUTH_REQUIRED=True` bo'lsa, qo'shimcha `X-Bot-Secret` header (backend `.env` dagi
  `BOT_API_SECRET` bilan bir xil) shart — aks holda 403. Bot `.env` ga `BOT_API_SECRET` qo'ying.
- `MemoryStorage`: bot qayta ishga tushsa FSM holati yo'qoladi; foydalanuvchi qaytadan tugmani bosadi.
- Matnlar o'zbek tilida, `parse_mode=HTML` (default) — foydalanuvchi matnini HTML'ga qo'shsangiz escape qiling.
- Python 3.12+ f-string ichida ichma-ich `"` ishlatmang (eski versiyalarda SyntaxError) — `display_name()` kabi
  oldindan o'zgaruvchiga yig'ing.

## 2026-09 o'zgarishlari

- Geo saqlangach xabar `GET /users/geo_recipients/` ro'yxatiga yuboriladi: adminlar + xodim viloyatiga javob
  beradigan menejerlar (`bot/services/user.py::get_geo_recipients`). Eski backend'da (404) `get_all_admins` ga qaytadi.
- Foydalanuvchiga javob matni «Kundalik vizit» bo'limiga yo'naltiradi (izoh majburiy).
- `display_name` HTML'ga `html.escape` bilan qo'yiladi.
