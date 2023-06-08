from aiogram.utils import executor
from settings import dp
import views

views.register_handlers_views(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
