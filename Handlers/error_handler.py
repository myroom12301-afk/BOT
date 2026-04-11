import asyncio
import logging
import traceback

from aiogram import Router
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import CallbackQuery, ErrorEvent, Message

from config import ADMIN_IDS
from servers import get_user_language

router = Router()
logger = logging.getLogger(__name__)

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


def _get_user_lang(user_id) -> str:
    lang = get_user_language(user_id)
    return lang if lang in error_text else "RU"


def _truncate_text(text: str, limit: int = 3500) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _build_admin_error_text(event: ErrorEvent) -> str:
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


def _get_bot_from_event(event: ErrorEvent):
    update = event.update
    if update.message is not None:
        return update.message.bot
    if update.callback_query is not None:
        return update.callback_query.bot
    return None


async def _notify_admins(event: ErrorEvent) -> None:
    bot = _get_bot_from_event(event)
    if bot is None:
        return
    admin_text = _build_admin_error_text(event)
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
        except TelegramForbiddenError:
            logger.warning("Admin %s blocked the bot — cannot send error report.", admin_id)
        except TelegramAPIError as e:
            logger.warning("Failed to send error report to admin %s: %s", admin_id, e)


async def _reply_to_user(event: ErrorEvent) -> None:
    update = event.update
    if update.message is not None:
        message: Message = update.message
        lang = _get_user_lang(message.from_user.id)
        try:
            await message.answer(error_text[lang])
        except TelegramAPIError:
            pass
        return
    if update.callback_query is not None:
        callback: CallbackQuery = update.callback_query
        lang = _get_user_lang(callback.from_user.id)
        try:
            await callback.answer(error_text[lang], show_alert=True)
        except TelegramAPIError:
            pass


@router.errors()
async def global_error_handler(event: ErrorEvent) -> bool:
    exc = event.exception

    # TelegramRetryAfter — flood control: wait and silently skip.
    if isinstance(exc, TelegramRetryAfter):
        retry_after = exc.retry_after
        await asyncio.sleep(retry_after)
        return True

    # Network errors, blocked bot, benign API quirks — not logic errors, skip silently.
    if isinstance(exc, (TelegramNetworkError, TelegramForbiddenError)):
        return True

    if isinstance(exc, TelegramBadRequest):
        msg = str(exc).lower()
        if any(
            phrase in msg
            for phrase in (
                "message is not modified",
                "message to delete not found",
                "message can't be deleted",
                "query is too old",
                "message to edit not found",
            )
        ):
            return True

    # Logic/unhandled errors — log and notify admins.
    logger.error("Unhandled bot error:", exc_info=exc)
    await _notify_admins(event)
    await _reply_to_user(event)
    return True