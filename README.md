# pharm_bot

Telegram bot for **Pharm**, a CRM for a pharmaceutical company's medical representatives. The
CRM itself is a Django REST API with a Telegram Mini App; this bot covers the one thing a Mini
App cannot do well — confirming a visit on the spot.

## What it does

1. A medical representative presses **📍 Joylashuv yuborish** (send location) and shares a live location.
2. The bot asks for a short video note from the place.
3. Location and video are saved in the backend (`POST /users/create_geo_location/`) and sent to
   every admin, so they can see where the visit happened.
4. The Mini App then lets the representative confirm the tour plan based on that location.

Users who are not registered in the backend are asked to sign up through the Mini App first.

## Stack

Python · aiogram 3 (FSM) · httpx · python-decouple

## Running locally

```bash
python -m venv .venv
.venv/Scripts/activate            # Windows; on Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # BOT_TOKEN is required; BACKEND_URL and BOT_API_SECRET optional
python main.py
```

Use Python 3.11 or 3.12: aiogram 3.22 has no wheels for Python 3.14 yet.
