import html
import logging

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
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
        "Manzilingizni yuborish uchun quyidagi tugmadan foydalaning 👇",
        reply_markup=user_menu_keyboard(),
    )


@router.message(F.text == "📍 Joylashuv yuborish")
async def start_geo_collection(message: types.Message, state: FSMContext):
    # Tugma avvaldan qolgan bo'lishi mumkin — xodim keyin bekor qilingan/o'chirilgan bo'lsa geo so'ralmaydi
    denied = access_denied_text(await get_user_by_chat(message.chat.id))
    if denied:
        await state.clear()
        return await message.answer(denied, reply_markup=ReplyKeyboardRemove())
    await message.answer("Iltimos, live location yuboring 📍")
    await state.set_state(GeoVideoState.waiting_for_location)


@router.message(GeoVideoState.waiting_for_location)
async def handle_location(message: types.Message, state: FSMContext):
    if not message.location:
        return await message.answer("❌ Iltimos, live location yuboring, oddiy emas 📍")

    if not message.location.live_period:
        return await message.answer("⚠️ Iltimos, <b>live location</b> yuboring ⏱")

    await state.update_data(lat=message.location.latitude, lon=message.location.longitude)
    await message.answer("✅ Joylashuv qabul qilindi!\nEndi videoni yuboring 🎥")
    await state.set_state(GeoVideoState.waiting_for_video)


@router.message(GeoVideoState.waiting_for_video)
async def handle_video_note(message: types.Message, state: FSMContext, bot: Bot):
    if not message.video_note:
        return await message.answer("⚠️ Iltimos, <b>video note</b> yuboring 🎥")

    data = await state.get_data()
    lat = data.get("lat")
    lon = data.get("lon")
    video_id = message.video_note.file_id

    if lat is None or lon is None:
        await state.clear()
        return await message.answer(
            "⚠️ Joylashuv topilmadi. Iltimos, «📍 Joylashuv yuborish» tugmasidan qaytadan boshlang."
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
