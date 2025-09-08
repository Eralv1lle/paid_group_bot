from aiogram import Router, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ChatJoinRequest, ContentType
from aiogram.enums import ParseMode

import json

from config import *
from keyboards import setup_join_kb


router = Router()

with open("pending_requests.json", "r", encoding="utf-8") as file:
    pending_requests = json.load(file)
pending_requests = {int(k): v for k, v in pending_requests.items()}
print(pending_requests)

@router.message(CommandStart())
async def handle_start(message: Message, bot: Bot):
    try:
        member = await bot.get_chat_member(GROUP_ID, message.from_user.id)

        if member.status in ("member", "administrator", "creator"):
            await message.answer("✅ Вы уже состоите в группе! Оплачивать ничего не нужно.")
            return

    except Exception as err:
        print(err)

    if message.from_user.id in pending_requests:
        await message.answer("Ваша заявка в обработке. Пожалуйста, ожидайте")
        return

    await message.answer(f"Здравствуйте, {message.from_user.first_name}! Если вы хотите вступить в группу, подайте заявку на вступление.")

@router.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest, bot: Bot):
    if join_request.chat.id != GROUP_ID:
        return

    user_id = join_request.from_user.id
    pending_requests[user_id] = {"id": user_id, "name": join_request.from_user.first_name}

    try:
        await bot.send_message(
            user_id,
            f"👋 Здравствуйте!\n"
            f"Чтобы вступить в нашу группу, необходимо внести оплату — *500 ₽*.\n\n"
            f"Способы оплаты:\n"
            f"💳 Карта: `1234 1234 1234 1234`\n"
            f"📲 СБП (по номеру): `+7 999 999 99 99`\n\n"
            f"✅ После оплаты прикрепите сюда чек (фото или документ), и мы подтвердим вашу заявку.",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as err:
        username = "" if not join_request.from_user.username else f", {join_request.from_user.username}"
        await bot.send_message(
            ADMIN_ID,
            f"Не удалось отправить сообщение пользователю {user_id}{username}. Возможно, он заблокировал бота."
        )
        print(err)

@router.message(F.from_user.id.in_(pending_requests), F.chat.type == "private")
async def handle_receipt(message: Message, bot: Bot):
    try:
        content_type = message.content_type

        if content_type == ContentType.TEXT:
            await bot.send_message(
                ADMIN_ID,
                f"Пользователь: {message.from_user.first_name}, прислал чек текстом:\n\n{message.html_text}",
                parse_mode=ParseMode.HTML,
                reply_markup=setup_join_kb(message.from_user.id)
            )
            await message.answer("✅ Отлично! Мы получили ваш чек.\n⏳ Пожалуйста, подождите — администратор проверит оплату и подтвердит заявку.")
        elif content_type == ContentType.PHOTO:
            await bot.send_photo(
                ADMIN_ID,
                photo=message.photo[-1].file_id,
                caption=f"{message.html_text}\n\nПользователь: {message.from_user.first_name}, прислал фото чека",
                parse_mode=ParseMode.HTML,
                reply_markup=setup_join_kb(message.from_user.id)
            )
            await message.answer("✅ Отлично! Мы получили ваш чек.\n⏳ Пожалуйста, подождите — администратор проверит оплату и подтвердит заявку.")
        elif content_type == ContentType.DOCUMENT:
            await bot.send_document(
                ADMIN_ID,
                document=message.document.file_id,
                caption=f"{message.html_text}\n\nПользователь: {message.from_user.first_name}, прислал чек документом",
                parse_mode=ParseMode.HTML,
                reply_markup=setup_join_kb(message.from_user.id)
            )
            await message.answer("✅ Отлично! Мы получили ваш чек.\n⏳ Пожалуйста, подождите — администратор проверит оплату и подтвердит заявку.")
        else:
            await message.answer("❗ Пожалуйста, отправьте чек в одном из форматов:\n📝 текст, 🖼 скриншот или 📄 документ.")

    except Exception as err:
        print(err)

@router.callback_query(F.data.startswith("confirm:"))
async def handle_confirm(callback: CallbackQuery, bot: Bot):
    user_id = int(callback.data.split(":")[1])
    user = pending_requests.get(user_id)

    try:
        await bot.approve_chat_join_request(GROUP_ID, user_id)
    except:
        pass

    await callback.answer(f"Пользователь: {user.get('name', 'Без имени')}, добавлен ✅")
    await callback.message.delete()

    await bot.send_message(
        user_id,
        "✅ Ваша заявка на вступление принята!\nДобро пожаловать в группу — теперь вы участник."
    )

    del pending_requests[user_id]

@router.callback_query(F.data.startswith("cancel:"))
async def handle_confirm(callback: CallbackQuery, bot: Bot):
    user_id = int(callback.data.split(":")[1])
    user = pending_requests.get(user_id)

    try:
        await bot.decline_chat_join_request(GROUP_ID, user_id)
    except:
        pass

    await callback.answer(f"Пользователь: {user.get('name', 'Без имени')}, отклонён ❌")
    await callback.message.delete()

    await bot.send_message(
        user_id,
        "❌ К сожалению, ваша заявка не была одобрена.\n💳 Пожалуйста, проверьте оплату и убедитесь, что чек отправлен корректно.\n\n🔄 Если произошла ошибка — просто подайте заявку снова и прикрепите чек ещё раз."
    )

    del pending_requests[user_id]
