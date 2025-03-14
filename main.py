import asyncio

from aiogram import Dispatcher
from botCommand import router, bot

async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())