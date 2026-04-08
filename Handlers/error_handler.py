import traceback

from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, ErrorEvent, Message

from config import ADMIN_IDS
from servers import get_user_language

router = Router()

error_text = {
    "RU": (
        "При обработке вашего запроса произошла ошибка.\n"
        "Пожалуйста, повторите попытку позже."
    ),
    "EN": (
        "An error occurred while processing your request.\n"
        "Please try again later."
    ),
    "KY": (
        "Сурамыңызды иштетүү учурунда ката кетти.\n"
        "Сураныч, бир аздан кийин кайра аракет кылып көрүңүз."
    ),
}


def _get_user_lang(user_id):
    lang = get_user_language(user_id)
    return lang if lang in error_text else "RU"


def _truncate_text(text, limit=3500):
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _build_admin_error_text(event: ErrorEvent):
    update = event.update
    user = None
    update_type = "unknown"
    payload = ""

    if update.message is not None:
        user = update.message.from_user
        update_type = "message"
        payload = update.message.text or update.message.caption or "<empty>"
    elif update.callback_query is not None:
        user = update.callback_query.from_user
        update_type = "callback_query"
        payload = update.callback_query.data or "<empty>"

    traceback_text = "".join(
        traceback.format_exception(
            type(event.exception),
            event.exception,
            event.exception.__traceback__,
        )
    )

    user_id = user.id if user is not None else "unknown"
    username = f"@{user.username}" if user is not None and user.username else "-"

    return _truncate_text(
        "\n".join(
            [
                "Unhandled bot error",
                f"update_type: {update_type}",
                f"user_id: {user_id}",
                f"username: {username}",
                f"payload: {payload}",
                "",
                traceback_text,
            ]
        )
    )


async def _send_error_message(message: Message):
    lang = _get_user_lang(message.from_user.id)
    await message.answer(error_text[lang])


async def _send_callback_error(callback: CallbackQuery):
    lang = _get_user_lang(callback.from_user.id)
    await callback.answer(error_text[lang], show_alert=True)


async def _notify_admins(event: ErrorEvent):
    admin_text = _build_admin_error_text(event)
    bot = None
    if event.update.message is not None:
        bot = event.update.message.bot
    elif event.update.callback_query is not None:
        bot = event.update.callback_query.bot
    if bot is None:
        return
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
        except TelegramAPIError as admin_error:
            print(f"Failed to send error notification to admin {admin_id}: {admin_error}")


@router.errors()
async def global_error_handler(event: ErrorEvent):
    print("Unhandled bot error:")
    traceback.print_exception(
        type(event.exception),
        event.exception,
        event.exception.__traceback__,
    )
    await _notify_admins(event)

    update = event.update
    if update.message is not None:
        await _send_error_message(update.message)
        return True

    if update.callback_query is not None:
        await _send_callback_error(update.callback_query)
        return True

    return True
