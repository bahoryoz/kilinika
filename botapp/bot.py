import os
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

from .api_client import APIClient

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
API_BASE_URL = os.getenv('BOT_API_BASE_URL', 'http://localhost:8000/api')

if not BOT_TOKEN:
    raise SystemExit('BOT_TOKEN bo\'sh. .env faylida Telegram tokenini kiriting yoki BOT_TOKEN ni to\'ldiring.')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class BookingStates(StatesGroup):
    choose_speciality = State()
    choose_doctor = State()
    choose_day = State()
    choose_slot = State()
    enter_complaint = State()
    confirm = State()


class UserData:
    def __init__(self):
        self.speciality_id = None
        self.speciality_name = None
        self.doctor_id = None
        self.doctor_name = None
        self.doctor_room = None
        self.doctor_price = None
        self.date = None
        self.slot_id = None
        self.slot_time = None
        self.complaint = ''


def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🏥 Navbat olish')],
            [KeyboardButton(text='❌ Bekor qilish')],
        ],
        resize_keyboard=True,
    )


async def send_specialities(message: types.Message, state: FSMContext):
    """Send specialities as inline buttons"""
    api = APIClient()
    specialities = await api.get_specialities()
    
    if not specialities:
        await message.answer('Xozircha yo\'nalishlar mavjud emas.')
        await state.clear()
        return

    buttons = [
        [InlineKeyboardButton(text=spec['name'], callback_data=f"spec_{spec['id']}")]
        for spec in specialities
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer('Yo\'nalishni tanlang:', reply_markup=keyboard)
    await state.set_state(BookingStates.choose_speciality)


@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Assalomu alaykum! 👋 Klinika navbati botiga xush kelibsiz.\n\nTanlang:',
        reply_markup=get_main_menu(),
    )


@dp.message(F.text == '🏥 Navbat olish')
async def booking_start(message: types.Message, state: FSMContext):
    await state.update_data(user_data=UserData())
    await send_specialities(message, state)


@dp.callback_query(BookingStates.choose_speciality)
async def choose_speciality(callback: types.CallbackQuery, state: FSMContext):
    spec_id = int(callback.data.split('_')[1])
    
    # Get speciality name
    api = APIClient()
    specs = await api.get_specialities()
    spec_name = next((s['name'] for s in specs if s['id'] == spec_id), 'Unknown')
    
    data = await state.get_data()
    user_data = data.get('user_data', UserData())
    user_data.speciality_id = spec_id
    user_data.speciality_name = spec_name
    
    # Get doctors
    doctors = await api.get_doctors(spec_id)
    
    if not doctors:
        await callback.message.answer('Bu yo\'nalishdagi shifokorlar mavjud emas.')
        await state.clear()
        await callback.message.answer('Asosiy menyu:', reply_markup=get_main_menu())
        return

    buttons = [
        [InlineKeyboardButton(text=f"{doc.get('doctor_name', 'Dr.')} - {doc['room']}", callback_data=f"doc_{doc['id']}")]
        for doc in doctors
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.answer(f'✅ {spec_name}\n\nShifokorni tanlang:', reply_markup=keyboard)
    await state.set_state(BookingStates.choose_doctor)
    await state.update_data(user_data=user_data)
    await callback.answer()


@dp.callback_query(BookingStates.choose_doctor)
async def choose_doctor(callback: types.CallbackQuery, state: FSMContext):
    doc_id = int(callback.data.split('_')[1])
    
    # Get doctor info
    api = APIClient()
    data = await state.get_data()
    user_data = data.get('user_data', UserData())
    doctors = await api.get_doctors(user_data.speciality_id)
    doc = next((d for d in doctors if d['id'] == doc_id), None)
    
    if not doc:
        await callback.message.answer('Shifokor topilmadi.')
        return

    user_data.doctor_id = doc_id
    user_data.doctor_name = doc.get('doctor_name', 'Dr.')
    user_data.doctor_room = doc['room']
    user_data.doctor_price = doc['price']
    
    # Get available days
    days = await api.get_available_days(doc_id)
    
    if not days:
        await callback.message.answer('Bu shifokorning bo\'sh kunlari mavjud emas.')
        return

    buttons = [
        [InlineKeyboardButton(text=day, callback_data=f"day_{day}")]
        for day in days[:7]  # Show first 7 days
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.answer(f"✅ {user_data.doctor_name} ({user_data.doctor_room})\n\nSanani tanlang:", reply_markup=keyboard)
    await state.set_state(BookingStates.choose_day)
    await state.update_data(user_data=user_data)
    await callback.answer()


@dp.callback_query(BookingStates.choose_day)
async def choose_day(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data.split('_')[1]
    
    # Get slots for this day
    api = APIClient()
    data = await state.get_data()
    user_data = data.get('user_data', UserData())
    
    slots = await api.get_slots(user_data.doctor_id, date)
    
    if not slots:
        await callback.message.answer('Bu kunda bo\'sh vaqtlar mavjud emas.')
        return

    user_data.date = date
    buttons = []
    for i, slot in enumerate(slots):
        button = InlineKeyboardButton(
            text=f"{slot['start_time']} - {slot['end_time']}",
            callback_data=f"slot_{slot['id']}"
        )
        if i % 2 == 0:
            buttons.append([button])
        else:
            buttons[-1].append(button)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.answer(f"✅ {date}\n\nVaqtni tanlang:", reply_markup=keyboard)
    await state.set_state(BookingStates.choose_slot)
    await state.update_data(user_data=user_data)
    await callback.answer()


@dp.callback_query(BookingStates.choose_slot)
async def choose_slot(callback: types.CallbackQuery, state: FSMContext):
    slot_id = int(callback.data.split('_')[1])
    
    # Get slot details
    api = APIClient()
    data = await state.get_data()
    user_data = data.get('user_data', UserData())
    
    slots = await api.get_slots(user_data.doctor_id, user_data.date)
    slot = next((s for s in slots if s['id'] == slot_id), None)
    
    if not slot:
        await callback.message.answer('Slot topilmadi.')
        return

    user_data.slot_id = slot_id
    user_data.slot_time = slot['start_time']
    
    await callback.message.answer('Shikoyatingizni yozing (yoki "O\'tkazib yuborish" deb yozing):')
    await state.set_state(BookingStates.enter_complaint)
    await state.update_data(user_data=user_data)
    await callback.answer()


@dp.message(BookingStates.enter_complaint)
async def enter_complaint(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_data = data.get('user_data', UserData())
    
    if message.text and message.text.lower() != "o'tkazib yuborish":
        user_data.complaint = message.text
    else:
        user_data.complaint = ''
    
    # Show confirmation
    await message.answer(
        f"📋 **Tasdiq**\n\n"
        f"🏥 Yo'nalish: {user_data.speciality_name}\n"
        f"👨‍⚕️ Shifokor: {user_data.doctor_name}\n"
        f"🏢 Xona: {user_data.doctor_room}\n"
        f"📅 Sana: {user_data.date}\n"
        f"🕐 Vaqt: {user_data.slot_time}\n"
        f"💰 Narx: {user_data.doctor_price} so'm\n"
        f"📝 Shikoyat: {user_data.complaint if user_data.complaint else '(mavjud emas)'}\n\n"
        f"To'g'rimi?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='✅ Ha, tasdiqlash', callback_data='confirm_yes')],
                [InlineKeyboardButton(text='❌ Yo\'q, bekor qilish', callback_data='confirm_no')],
            ]
        )
    )
    await state.set_state(BookingStates.confirm)
    await state.update_data(user_data=user_data)


@dp.callback_query(BookingStates.confirm)
async def confirm_appointment(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'confirm_no':
        await callback.message.answer('Bekor qilindi. Asosiy menyu:', reply_markup=get_main_menu())
        await state.clear()
        await callback.answer()
        return

    data = await state.get_data()
    user_data = data.get('user_data', UserData())
    
    # For now, we'll just show success since we don't have real user auth
    await callback.message.answer(
        f"✅ **Navbat band qilindi!**\n\n"
        f"Shifokor: {user_data.doctor_name}\n"
        f"Sana: {user_data.date}\n"
        f"Vaqt: {user_data.slot_time}\n"
        f"Xona: {user_data.doctor_room}\n\n"
        f"Qabul vaqtidan 2 soat oldin bekor qila olasiz.",
        reply_markup=get_main_menu()
    )
    
    await state.clear()
    await callback.answer()


@dp.message(F.text == '📋 Mening navbatlarim')
async def my_appointments(message: types.Message, state: FSMContext):
    await message.answer(
        'Mening navbatlarim bo\'limi hozircha ishga tayyorlanmoqda.\n\n'
        'Navbatlarni ko\'rish va bekor qilish uchun biroz kuting.',
        reply_markup=get_main_menu()
    )
    await state.clear()


@dp.message(F.text == '❌ Bekor qilish')
async def cancel_appointment(message: types.Message, state: FSMContext):
    await message.answer(
        'Bekor qilish bo\'limi hozircha ishga tayyorlanmoqda.\n\n'
        'Navbatni bekor qilish uchun biroz kuting.',
        reply_markup=get_main_menu()
    )
    await state.clear()


@dp.message()
async def echo(message: types.Message, state: FSMContext):
    await message.answer('Buyruqni tushunmadim. /start yoki menyu tugmasini bosing.', reply_markup=get_main_menu())
    await state.clear()


async def main():
    print("🤖 Bot ishga tushmoqda...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
