import os
import logging
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
import requests

API_TOKEN = os.environ.get('API_TOKEN', '6109070512:AAGBUfYo3-MKwQV7rhiHQ6Jp9ahC2LJ9D_A')
WEB_APP_URL = os.environ.get('WEB_APP_URL', 'https://privatizerbot.herokuapp.com')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

state = {}

async def on_start(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Создать Privacy Policy", callback_data="create_privacy_policy"),
        InlineKeyboardButton("Создать Terms of Use", callback_data="create_terms_of_use"),
    )
    await message.reply("Продолжите фразу: «Сегодня я хочу...»", reply_markup=markup)

async def on_callback_query(call: types.CallbackQuery):
    action = call.data
    chat_id = call.message.chat.id

    if action == "create_privacy_policy":
        state[chat_id] = {"step": 1, "document_type": "privacy_policy"}
        await call.message.reply("Введите имя разработчика:")
    elif action == "create_terms_of_use":
        state[chat_id] = {"step": 1, "document_type": "terms_of_use"}
        await call.message.reply("Введите имя разработчика:")

async def on_message(message: types.Message):
    chat_id = message.chat.id

    if chat_id not in state:
        return

    step = state[chat_id]["step"]

    if step == 1:
        state[chat_id]["developer_name"] = message.text
        state[chat_id]["step"] = 2
        await message.reply("Введите название приложения:")
    elif step == 2:
        state[chat_id]["app_name"] = message.text
        state[chat_id]["step"] = 3
        await message.reply("Введите ваш email:")
    elif step == 3:
        state[chat_id]["email"] = message.text
        document_type = state[chat_id]["document_type"]

        response = requests.post(
            f"{WEB_APP_URL}/api/create_document",
            json={
                "document_type": document_type,
                "app_name": state[chat_id]["app_name"],
                "developer_name": state[chat_id]["developer_name"],
                "email": state[chat_id]["email"],
            },
        )
        try:
            response.raise_for_status()
            response_json = response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Ошибка: {e}")
            await message.reply("Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз.")
            return
        except ValueError as e:
            print(f"Ошибка: {e}")
            await message.reply("Произошла ошибка при обработке ответа сервера. Пожалуйста, попробуйте еще раз.")
            return

        document_url = f"{WEB_APP_URL}{response_json['url']}"
        await message.reply(f"Ваша ссылка на {document_type.replace('_', ' ').capitalize()}: {document_url}")
        del state[chat_id]

if __name__ == '__main__':
    from aiogram import executor
    from aiogram.contrib.middlewares.logging import LoggingMiddleware

    dp.middleware.setup(LoggingMiddleware())

    dp.register_message_handler(on_start, commands=['start'])
    dp.register_message_handler(on_message)
    dp.register_callback_query_handler(on_callback_query)

    executor.start_polling(dp, skip_updates=True)
