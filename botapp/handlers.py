from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


async def handle_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Mavjud buyruqlar: /start')


async def handle_unknown(message: Message):
    await message.answer('Bu buyruq tanimlanmagan. /start buyrug\'ini ishlating.')
