import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
API_BASE_URL = os.getenv('BOT_API_BASE_URL', 'http://localhost:8000/api')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class BookingStates(StatesGroup):
    choose_speciality = State()
    choose_doctor = State()
    choose_day = State()
    choose_slot = State()
    enter_complaint = State()
    confirm = State()


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Navbat olish'), KeyboardButton(text='Mening navbatlarim')],
            [KeyboardButton(text='Bekor qilish')],
        ],
        resize_keyboard=True,
    )


@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Assalomu alaykum! Klinika navbati botiga xush kelibsiz.\n\nTanlang:',
        reply_markup=main_menu(),
    )


@dp.message(lambda message: message.text == 'Navbat olish')
async def booking_start(message: types.Message, state: FSMContext):
    await message.answer('Yo\'nalishni tanlang:')
    await state.set_state(BookingStates.choose_speciality)


@dp.message(lambda message: message.text == 'Mening navbatlarim')
async def my_appointments(message: types.Message):
    await message.answer('Mening navbatlarim bo\'limi hozircha ishga tayyorlanmoqda. API bilan bog\'lanish tuzilmoqda.')


@dp.message(lambda message: message.text == 'Bekor qilish')
async def cancel_booking(message: types.Message):
    await message.answer('Bekor qilish uchun mavjud navbatlarni ko\'rib chiqish texnik ishlov berishda.')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
