from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ContentType
from servers import get_user_language
router = Router()

unsupported_content_text = {
    "RU": "Этот тип сообщения пока не поддерживается. Пожалуйста, используйте текст или кнопки ниже.",
    "EN": "This type of message is not supported yet. Please use text or the buttons below.",
    "KY": "Бул түрдөгү билдирүү азырынча колдоого алынбайт. Сураныч, текст жазыңыз же төмөнкү баскычтарды колдонуңуз."
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

@router.message(F.content_type.in_(UNSUPPORTED_TYPES))
async def unsupported_content_handler(message: Message):
    lang = get_user_language(message.from_user.id)
    await message.answer(unsupported_content_text.get(lang, unsupported_content_text["RU"]))