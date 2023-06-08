from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
import os
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

