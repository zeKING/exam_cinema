from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

movies = KeyboardButton('Фильмы')
sessions = KeyboardButton('Сеансы')
tickets = KeyboardButton('Мои билеты')
back = KeyboardButton('🔙 Назад')

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(movies, sessions).row(tickets, back)
