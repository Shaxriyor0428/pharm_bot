import html
import logging

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot.keyboard import user_menu_keyboard
from bot.services.geo_location import create_geo_location
from bot.services.user import get_geo_recipients, get_user_by_chat
from bot.state import GeoVideoState

logger = logging.getLogger(__name__)

router = Router()

NOT_REGISTERED_TEXT = "Iltimos avval web app orqali ro'yxatdan o'ting 👇"
NOT_ACCEPTED_TEXT = "⏳ So'rovingiz hali admin tomonidan tasdiqlanmagan. Iltimos, kuting."
# Ishlamaydigan xodim (admin «Bekor qilingan» qilgan) — "kuting" emas, tugma ham olib tashlanadi
REJECTED_TEXT = "⛔️ Akkauntingiz faol emas (bekor qilingan). Savol bo'lsa rahbariyatga murojaat qiling."

# Bot tugmasi (request_location) faqat ODDIY joylashuv yuboradi — jonli joylashuvni Telegram faqat 📎 menyusidan
# yuborishga ruxsat beradi. Shuning uchun aniq ko'rsatma (mijoz shikoyati 2026-10-16: lokatsiya qabul qilinmayapti).
LIVE_HELP = (
    "📍 <b>Jonli joylashuvni yuborish:</b>\n"
    "1. Xabar yozish joyidagi 📎 (skrepka) belgisini bosing\n"
    "2. «Joylashuv» (Location / Геопозиция) ni tanlang\n"
    "3. «Jonli joylashuvni ulashish» (Share Live Location / Транслировать геопозицию) ni bosing\n"
    "4. Muddatni tanlang (15 daqiqa yetarli) va yuboring\n\n"
    "⚠️ Oddiy joylashuv (joriy joylashuv yoki xaritadan tanlangan nuqta) qabul qilinmaydi."
)
VIDEO_HELP = (
    "🎥 Endi <b>dumaloq video</b> (video xabar) yuboring: xabar yozish joyidagi 🎤 mikrofon belgisini bir marta "
    "bosing — 📷 kameraga almashadi, keyin uni bosib turib video yozing."
)


def access_denied_text(user: dict | None) -> str | None:
    """Geo yubora olmaydigan foydalanuvchi uchun javob matni; ruxsat bo'lsa None."""
    if not user:
        return NOT_REGISTERED_TEXT
    status = user.get("status")
    if status == "rejected":
        return REJECTED_TEXT
    if status != "accepted":
        return NOT_ACCEPTED_TEXT
    return None


def display_name(user: dict) -> str:
    """Foydalanuvchining ko'rsatiladigan ismi (first_name + last_name, bo'lmasa username)."""
    full_name = " ".join(
        part for part in (user.get("first_name"), user.get("last_name")) if part
    ).strip()
    return full_name or user.get("username") or f"chat_id {user.get('chat_id')}"


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()

    denied = access_denied_text(await get_user_by_chat(message.chat.id))
    if denied:
        return await message.answer(denied, reply_markup=ReplyKeyboardRemove())

    return await message.answer(
        "Ishga kelganingizni belgilash uchun jonli joylashuv va dumaloq video yuboring.\n"
        "«📍 Joylashuv yuborish» tugmasini bosing yoki to'g'ridan-to'g'ri jonli joylashuv yuboring 👇",
        reply_markup=user_menu_keyboard(),
    )


@router.message(F.text == "📍 Joylashuv yuborish")
async def start_geo_collection(message: types.Message, state: FSMContext):
    # Tugma avvaldan qolgan bo'lishi mumkin — xodim keyin bekor qilingan/o'chirilgan bo'lsa geo so'ralmaydi
    denied = access_denied_text(await get_user_by_chat(message.chat.id))
    if denied:
        await state.clear()
        return await message.answer(denied, reply_markup=ReplyKeyboardRemove())
    await message.answer(LIVE_HELP)
    await state.set_state(GeoVideoState.waiting_for_location)


@router.message(F.location)
async def handle_location(message: types.Message, state: FSMContext):
    """
    Jonli joylashuv — istalgan holatda qabul qilinadi: tugmani bosmasdan to'g'ridan-to'g'ri yuborilsa ham
    (avval bot jim turardi — "keldi" belgilanmasdi). Oddiy va forward qilingan joylashuv — rad, ko'rsatma bilan.
    """
    denied = access_denied_text(await get_user_by_chat(message.chat.id))
    if denied:
        await state.clear()
        return await message.answer(denied, reply_markup=ReplyKeyboardRemove())

    if message.forward_origin is not None:
        await state.set_state(GeoVideoState.waiting_for_location)
        return await message.answer(
            "⚠️ Boshqa xabardan forward qilingan joylashuv qabul qilinmaydi — o'zingiz yuboring.\n\n" + LIVE_HELP
        )

    if not message.location.live_period:
        await state.set_state(GeoVideoState.waiting_for_location)
        return await message.answer(
            "⚠️ Bu <b>oddiy</b> joylashuv — faqat <b>jonli</b> joylashuv qabul qilinadi.\n\n" + LIVE_HELP
        )

    await state.update_data(lat=message.location.latitude, lon=message.location.longitude)
    await state.set_state(GeoVideoState.waiting_for_video)
    await message.answer("✅ Jonli joylashuv qabul qilindi!\n\n" + VIDEO_HELP)


@router.message(GeoVideoState.waiting_for_location)
async def waiting_location_hint(message: types.Message):
    await message.answer(LIVE_HELP)


@router.message(StateFilter(None), F.video_note)
async def video_without_location(message: types.Message):
    # Avval joylashuv yuborilmagan (yoki bot qayta ishga tushib holat yo'qolgan) — jim turmaymiz
    await message.answer("⚠️ Avval jonli joylashuvni yuboring, keyin dumaloq videoni.\n\n" + LIVE_HELP)


@router.message(GeoVideoState.waiting_for_video)
async def handle_video_note(message: types.Message, state: FSMContext, bot: Bot):
    if not message.video_note:
        if message.video:
            return await message.answer("⚠️ Bu oddiy video — <b>dumaloq video</b> kerak.\n\n" + VIDEO_HELP)
        return await message.answer(VIDEO_HELP)

    data = await state.get_data()
    lat = data.get("lat")
    lon = data.get("lon")
    video_id = message.video_note.file_id

    if lat is None or lon is None:
        await state.clear()
        return await message.answer(
            "⚠️ Joylashuv topilmadi. Iltimos, jonli joylashuvni qaytadan yuboring.\n\n" + LIVE_HELP
        )

    # --- backend'ga saqlaymiz ---
    saved = await create_geo_location(lat, lon, video_id, chat_id=message.chat.id)
    if not saved:
        await state.clear()
        return await message.answer(
            "❌ Joylashuvni saqlab bo'lmadi. Akkauntingiz tasdiqlanganini tekshiring "
            "yoki birozdan so'ng qayta urinib ko'ring."
        )

    # --- foydalanuvchiga javob ---
    await message.answer(
        "✅ Joylashuv va video muvaffaqiyatli saqlandi!\n"
        "Rahmat 🙌\n\nEndi web app'dagi «Kundalik vizit» bo'limida shifokor/dorixonaga tashrifni "
        "«Bajarildi» qilib, izoh yozing (nima muhokama qilindi, qaysi dori taklif qilindi)."
    )

    await state.clear()

    # --- adminlar va viloyat menejerlariga yuboramiz ---
    user = await get_user_by_chat(message.chat.id) or {"chat_id": message.chat.id}
    admins = await get_geo_recipients(message.chat.id)
    if not admins:
        return None

    text = (
        f"🆕 <b>Yangi joylashuv va video!</b>\n\n"
        f"👤 Foydalanuvchi: {html.escape(display_name(user))}\n"
        f"📍 Koordinatalar: {lat}, {lon}\n"
        f"🌐 <a href='https://www.google.com/maps?q={lat},{lon}'>Google xaritada ochish</a>"
    )

    for admin in admins:
        admin_chat_id = admin.get("chat_id")
        if not admin_chat_id:
            continue
        try:
            # 1️⃣ Text yuborish
            await bot.send_message(
                chat_id=admin_chat_id,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )

            # 2️⃣ Video yuborish
            await bot.send_video_note(chat_id=admin_chat_id, video_note=video_id)

            # 3️⃣ Location yuborish
            await bot.send_location(chat_id=admin_chat_id, latitude=lat, longitude=lon)

        except Exception as e:
            # Telegram BadRequest: chat not found (admin botni start qilmagan) bo'lsa davom etadi
            logger.warning("Admin %s ga yuborishda xatolik: %s", admin.get("id"), e)
            continue
