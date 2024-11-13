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

# Приветственное сообщение и кнопка для присоединения к тестированию
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
                "В течение всего 2023 года мы активно играли в такие игры, как **MINES** и **Lucky Jet** на платформе 1win, собирая результаты, чтобы разработать алгоритм, способный распознавать паттерны и предсказывать будущие результаты с максимальной точностью.\n\n"
                "🎉 Мы достигли успеха, и теперь планируем выпустить нашу программу в продажу в середине **2025 года** за значительную цену. Но сейчас у вас есть уникальная возможность поучаствовать в **открытом тестировании** нашей программы и получить к ней доступ совершенно бесплатно!\n\n"
                "Нажмите на кнопку ниже, чтобы присоединиться к тестированию."
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
                "🎉 Отлично, мы рады, что вы решили принять участие в тестировании нашего приложения! 🚀\n\n"
                "Для того, чтобы начать пользоваться нашим приложением, вам потребуется аккаунт на сайте **1win**.\n\n"
                "⚠️ **Обратите внимание**: чтобы наша программа могла отслеживать ваш аккаунт, он должен быть **зарегистрирован с использованием нашего промокода** — **GPT24**. В противном случае программа не сможет найти ваш аккаунт и предоставить доступ к функциональности.\n\n"
                "Пожалуйста, зарегистрируйтесь, используя кнопку ниже, и после этого нажмите «Проверить регистрацию»."
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
            caption=(
                "🔍 Пожалуйста, введите **ID вашего аккаунта на 1win** для проверки регистрации.\n\n"
                "📌 Вы можете найти свой ID в личном кабинете на сайте 1win. После ввода ID нажмите «Отправить», чтобы мы проверили его в нашей системе."
            )
        )
    users[callback_query.message.chat.id] = 'awaiting_id'

# Обработка ввода ID пользователя
@dp.message_handler(lambda message: users.get(message.chat.id) == 'awaiting_id')
async def process_user_id(message: types.Message):
    user_id = message.text.strip()
    
    # Отправка запроса на сервер для проверки ID
    try:
        response = requests.get(POSTBACK_API_URL)
        response.raise_for_status()
        data = response.json()

        if any(user.get("user_id") == user_id for user in data):
            await message.answer(
                "✅ **Аккаунт найден!** 🎉\n\n"
                "Теперь вы можете приступить к работе с нашим приложением. 🚀\n\n"
                "Для этого нажмите на кнопку ниже и запустите приложение.",
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("📱 Запустить приложение", url="https://t.me/redsofts_bot/soft")
                )
            )
        else:
            await message.answer(
                "❌ **ID не найден**.\n\n"
                "Пожалуйста, убедитесь, что ваш аккаунт был **зарегистрирован по нашему промокоду GPT24**, и попробуйте ввести ваш ID снова. 🔄"
            )
    except requests.exceptions.RequestException as e:
        await message.answer(
            f"⚠️ Произошла ошибка при проверке вашего ID. Пожалуйста, попробуйте позже. Ошибка: {e}"
        )

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
