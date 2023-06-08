import re
from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import bot, dp
# from keyboards.lang_kb import kb_lang
from keyboards.menu_kb import menu_kb
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import *
from datetime import timedelta
import requests

# base_url = 'http://127.0.0.1:8000/api/v1/'
base_url = 'https://test.ai-softdev.com/api/v1/'
def ticket_kb(obj, text):
    kb = InlineKeyboardButton(text, callback_data=f'ticket_cancel {obj["id"]}')
    return InlineKeyboardMarkup().add(kb)


def session_kb(obj, text):
    kb = InlineKeyboardButton(text, callback_data=f'session_detail {obj["id"]}')
    return InlineKeyboardMarkup().add(kb)


def movie_kb(obj, text):
    kb = InlineKeyboardButton(text, callback_data=f'movie_detail {obj["id"]}')
    return InlineKeyboardMarkup().add(kb)


def validate_uzb_phone(value):
    if len(value) != 13:
        raise ValueError('Error')
    if value[:4] != '+998':
        raise ValueError('Error')
    return value


def ticket_pretty(obj):
    date_time = datetime.strptime(obj['session_time'][:-6], "%Y-%m-%dT%H:%M:%S")
    return f"{obj['movie_name']}, {str(date_time.hour).rjust(2, '0')}:" \
                f"{str(date_time.minute//10).ljust(2, '0')}, {obj['hall_name']}, {obj['row']} ряд, {obj['seat']} место"


def session_pretty(obj, has_movie=False):
    date_time = datetime.strptime(obj['time'][:-6], "%Y-%m-%dT%H:%M:%S")
    text = f"{obj['hall_name']}, {str(date_time.hour).rjust(2, '0')}:" \
                f"{str(date_time.minute//10).ljust(2, '0')}"
    if not has_movie:
        text = f"{obj['movie_name']}, " + text
    return text


def movie_pretty(obj):
    return f"{obj['name']}, {obj['age_limit']}+, длительность: {obj['duration']} мин."


class Form(StatesGroup):
    session_id = State()
    row = State()
    seat = State()
    phone = State()




async def start(message: types.Message):
    print(message.from_user.id)
    await bot.send_message(message.from_user.id, text=f'Чувак {message.from_user.first_name}, могу помочь?!',
                               reply_markup=menu_kb.menu_kb)
    state = dp.get_current().current_state()
    await state.finish()

    # await message.reply('Не чувак ни чем не могу не помочь')


async def movie(message: types.Message):
    print(message.from_user.id)
    movies = requests.get(f'{base_url}movie?page=1&limit=30').json()

    for mov in movies['results']:
        text = movie_pretty(mov)
        await bot.send_message(message.from_user.id, text=text, reply_markup=movie_kb(mov, '➡️'))
    if not movies['results']:
        await bot.send_message(message.from_user.id, text='Фильмов нет')

async def movie_detail(callback_query: types.CallbackQuery):
    movie_id = int(callback_query.data.split()[1])
    sessions = requests.get(f'{base_url}session?movie={movie_id}&page=1&limit=30').json()
    text = ''
    if sessions['results']:
        text = 'Выберите сеанс'
    else:
        text = f"Сеансов на этот фильм нет"
    await bot.send_message(callback_query.from_user.id, text=text)
    for ses in sessions['results']:
        text = session_pretty(ses, has_movie=True)
        await bot.send_message(callback_query.from_user.id, text=text, reply_markup=session_kb(ses, '➡️'))



async def session(message: types.Message):
    sessions = requests.get(f'{base_url}session').json()

    text = ''
    for ses in sessions['results']:
        text = session_pretty(ses)
        await bot.send_message(message.from_user.id, text=text, reply_markup=session_kb(ses, '➡️'))
    if not text:
        text = 'Сеансов нет'

# https://test.ai-softdev.com
async def session_detail(callback_query: types.CallbackQuery):
    session_id = int(callback_query.data.split()[1])
    session_obj = requests.get(f'{base_url}session/{session_id}').json()
    # await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, text=f'Вы выбрали: {session_pretty(session_obj)}\nВыберите '
                                                             f'место.')
    data = requests.get(f'{base_url}ticket?session={session_id}').json()
    row_len = len(data['rows'][1])
    text = '-'*(row_len - 3) + 'Экран' + '-'*(row_len - 3) + '\n'
    for row in data['rows']:
        for seat in row:
            text += '* ' if seat['status'] != 0 else '0 '
        text += '\n'
    text += '0 - свободно, * - занято'
    await bot.send_message(callback_query.from_user.id, text=text)
    await bot.send_message(callback_query.from_user.id, text='Введите ряд')
    await Form.session_id.set()
    state = dp.get_current().current_state()
    async with state.proxy() as data:
        data['session_id'] = session_id
    await Form.next()


async def row(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            data['row'] = int(message.text)
        except ValueError:
            await state.finish()
            await bot.send_message(message.from_user.id, text='Неверный ряд')
            return
    await bot.send_message(message.from_user.id, text='Введите место')
    await Form.next()


async def seat(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            data['seat'] = int(message.text)
        except ValueError:
            await state.finish()
            await bot.send_message(message.from_user.id, text='Неверное место')
            return
    await bot.send_message(message.from_user.id, text='Введите номер телефона (В формате +998999999999)')
    await Form.next()

async def phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            phone_num = re.sub(r'[() -]', '', message.text)
            data['phone'] = validate_uzb_phone(phone_num)
            send = {'session_id': data['session_id'], 'row': data['row'], 'seat': data['seat'], 'phone': data['phone'],
                    'user_id': message.from_user.id}
            await state.finish()

            res = requests.post(f'{base_url}ticket/create', data=send).json()

            await bot.send_message(message.from_user.id, text=res['message'])




        except ValueError:
            await state.finish()
            await bot.send_message(message.from_user.id, text='Неверный номер')
            return



async def ticket(message: types.Message):
    tickets = requests.get(f'{base_url}ticket/my?page=1&limit=30', data={'user_id':
                                                                                     message.from_user.id}).json()
    for tick in tickets['results']:
        text = ticket_pretty(tick)
        await bot.send_message(message.from_user.id, text=text, reply_markup=ticket_kb(tick, '❌'))
    if not tickets['results']:
        await bot.send_message(message.from_user.id, text='У вас пока нет приобретенных билетов')


async def ticket_cancel(callback_query: types.CallbackQuery):
    ticket_id = int(callback_query.data.split()[1])
    tick = requests.delete(f'{base_url}ticket/delete/{ticket_id}', data={'user_id':
                                                                                    callback_query.from_user.id}).json()
    print(tick)
    await bot.send_message(callback_query.from_user.id, text='Вы отменили билет')

def register_handlers_views(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(start, Text(contains='🔙'))
    dp.register_message_handler(movie, Text(contains='Фильмы'))
    dp.register_message_handler(session, Text(contains='Сеансы'))
    dp.register_message_handler(ticket, Text(contains='Мои билеты'))
    dp.register_callback_query_handler(movie_detail, lambda c: c.data.split()[0] == 'movie_detail')
    dp.register_callback_query_handler(session_detail, lambda c: c.data.split()[0] == 'session_detail')
    dp.register_callback_query_handler(ticket_cancel, lambda c: c.data.split()[0] == 'ticket_cancel')
    # dp.register_message_handler(session_id, state=Form.session_id)
    dp.register_message_handler(row, state=Form.row)
    dp.register_message_handler(seat, state=Form.seat)
    dp.register_message_handler(phone, state=Form.phone)
