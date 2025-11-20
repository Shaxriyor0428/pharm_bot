from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboard import user_menu_keyboard
from bot.services.geo_location import create_geo_location
from bot.services.user import get_user_by_chat, get_all_admins
from bot.state import GeoVideoState

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    user = await get_user_by_chat(message.chat.id)
    if not user:
        return await message.answer("Iltimos avval web app orqali ro'yxatdan o'ting 👇")

    return await message.answer(
        "Manzilingizni yuborish uchun quyidagi tugmadan foydalaning 👇",
        reply_markup=user_menu_keyboard()
    )


@router.message(F.text == "📍 Joylashuv yuborish")
async def start_geo_collection(message: types.Message, state: FSMContext):
    await message.answer("Iltimos, live location yuboring 📍", reply_markup=None)
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
    user = await get_user_by_chat(message.chat.id)
    video_id = message.video_note.file_id

    # --- bazaga saqlaymiz ---
    await create_geo_location(lat, lon, video_id, user)

    # --- foydalanuvchiga javob ---
    await message.answer(
        "✅ Joylashuv va video muvaffaqiyatli saqlandi!\n"
        "Rahmat 🙌\n\nWeb appga kirib belgilang — qaysi shifokor yoki klinikaga kelganingizni."
    )

    await state.clear()

    # --- adminlarga yuboramiz ---
    admins = await get_all_admins()
    if not admins:
        return

    text = (
        f"🆕 <b>Yangi joylashuv va video!</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name + ' ' + user.last_name or user.username}\n"
        f"📍 Koordinatalar: {lat}, {lon}\n"
        f"🌐 <a href='https://www.google.com/maps?q={lat},{lon}'>Google xaritada ochish</a>"
    )

    for admin in admins:
        try:
            # 1️⃣ Text yuborish
            await bot.send_message(
                chat_id=admin.chat_id,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )

            # 2️⃣ Video yuborish
            await message.bot.send_video_note(chat_id=admin.chat_id, video_note=video_id)

            # 3️⃣ Location yuborish
            await bot.send_location(
                chat_id=admin.chat_id,
                latitude=lat,
                longitude=lon
            )

        except Exception as e:
            print(f"⚠️ Admin {admin.id} ga yuborishda xatolik: {e}")


