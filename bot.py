import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Токен вашего бота
API_TOKEN = '7249249749:AAHPpuPqSQp48okFcXkXDC7vLSdfEpmVrEM'
POSTBACK_API_URL = "https://postback-server-boba.onrender.com/data"

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Логирование
logging.basicConfig(level=logging.INFO)

# Состояние пользователей для ввода ID
users = {}

# Команда /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    join_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🚀 Присоединиться к тестированию", callback_data='join')
    )
    with open("redsoftpage.png", 'rb') as photo:
        await bot.send_photo(
            message.chat.id,
            photo=photo,
            caption=(
                "👋 Добро пожаловать!\n\n"
                "Мы — команда **RED SOFT** 🚀, которая занимается разработкой вычислительных алгоритмов для различных задач.\n\n"
                "📊 Весь 2023 год мы активно играли в такие игры, как **MINES** и **Lucky Jet** на платформе 1win, собирая результаты для разработки алгоритма, предсказывающего результаты с высокой точностью.\n\n"
                "Сейчас у вас есть возможность участвовать в **открытом тестировании** бесплатно! 🎉"
            ),
            reply_markup=join_button
        )

# Обработка нажатия на кнопку "Присоединиться к тестированию"
@dp.callback_query_handler(lambda c: c.data == 'join')
async def process_join(callback_query: types.CallbackQuery):
    registration_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔗 Зарегистрироваться на 1win", url="https://1wbhk.com/casino/list?open=register&p=24h6"),
        InlineKeyboardButton("✅ Проверить регистрацию", callback_data='check_registration')
    )
    with open("instruction.png", 'rb') as photo:
        await bot.send_photo(
            callback_query.message.chat.id,
            photo=photo,
            caption=(
                "🎉 Спасибо за ваше участие!\n\n"
                "Для начала работы нужен аккаунт на **1win**.\n\n"
                "⚠️ **Важно**: зарегистрируйтесь по нашему промокоду **GPT24**.\n"
                "После регистрации нажмите «Проверить регистрацию»."
            ),
            reply_markup=registration_button
        )

# Обработка нажатия на кнопку "Проверить регистрацию"
@dp.callback_query_handler(lambda c: c.data == 'check_registration')
async def check_registration(callback_query: types.CallbackQuery):
    with open("id.png", 'rb') as photo:
        await bot.send_photo(
            callback_query.message.chat.id,
            photo=photo,
            caption="🔍 Введите **ID вашего аккаунта на 1win**:"
        )
    users[callback_query.message.chat.id] = 'awaiting_id'

# Обработка ввода ID пользователя
@dp.message_handler(lambda message: users.get(message.chat.id) == 'awaiting_id')
async def process_user_id(message: types.Message):
    user_id = message.text.strip()
    
    # Отправка запроса на сервер для проверки ID
    response = requests.get(POSTBACK_API_URL)
    if response.status_code == 200:
        data = response.json()
        if any(user.get("user_id") == user_id for user in data):
            await message.answer(
                "✅ **Аккаунт найден!** 🎉\n\n"
                "Теперь вы можете приступить к работе с нашим приложением. 🚀",
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("📱 Запустить приложение", url="https://t.me/redsofts_bot/soft")
                )
            )
        else:
            await message.answer("❌ **ID не найден**. Проверьте ваш промокод и введите ID снова. 🔄")
    else:
        await message.answer("⚠️ Ошибка сервера. Попробуйте позже.")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
