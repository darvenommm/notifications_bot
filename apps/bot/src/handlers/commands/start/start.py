from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.src.handlers.commands import commands_router


@commands_router.message(CommandStart())
async def start_handler(message: Message) -> None:
    print("start_handler")
