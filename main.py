import logging

from aiogram import Bot, Dispatcher
from config import TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
from Handlers.admin_cons import router as admin_cons_router
from Handlers.error_handler import router as error_router
from Handlers.start import router as start_router
from Handlers.callback_data import router as callback_router
from Handlers.main_choose import router as about_college_router
from Handlers.about_college_etc import router as etc_router
import asyncio
from servers import init_db
from Handlers.about_admis import router as admis_router
from Handlers.about_cons import router as cons_router
from aiogram.fsm.storage.memory import MemoryStorage
from Handlers.fsm_cb import router as fsm_router
from Handlers.Unsuport_type import router as filter_router
bot = Bot(token=TOKEN)
disp = Dispatcher(storage=MemoryStorage())

init_db()


async def main():
    disp.include_router(error_router)
    disp.include_router(filter_router)
    disp.include_router(start_router)
    disp.include_router(admin_cons_router)
    disp.include_router(fsm_router)
    disp.include_router(callback_router)
    disp.include_router(about_college_router)
    disp.include_router(admis_router)
    disp.include_router(cons_router)
    disp.include_router(etc_router)
    await disp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())