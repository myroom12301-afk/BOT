from aiogram import Router, F
from aiogram.fsm.scene import StateFilter
from aiogram.types import Message
from aiogram.enums import ContentType
from servers import get_user_language
router = Router()

unsupported_content_text = {
    "RU": "Данный тип сообщения в настоящее время не поддерживается. Пожалуйста, используйте текстовые сообщения или кнопки меню.",
    "EN": "This type of message is not currently supported. Please use text messages or the menu buttons.",
    "KY": "Билдирүүнүн бул түрү азырынча колдоого алынбайт. Сураныч, тексттик билдирүүлөрдү же меню баскычтарын колдонуңуз."
}

UNSUPPORTED_TYPES = [
    ContentType.PHOTO,
    ContentType.VIDEO,
    ContentType.VOICE,
    ContentType.VIDEO_NOTE,
    ContentType.DOCUMENT,
    ContentType.STICKER,
    ContentType.ANIMATION,
    ContentType.AUDIO,
    ContentType.CONTACT,
    ContentType.LOCATION,
    ContentType.VENUE,
    ContentType.POLL,
    ContentType.DICE,
]

@router.message(F.content_type.in_(UNSUPPORTED_TYPES), StateFilter(None))
async def unsupported_content_handler(message: Message):
    lang = get_user_language(message.from_user.id)
    await message.answer(unsupported_content_text.get(lang, unsupported_content_text["RU"]))
