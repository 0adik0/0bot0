import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiohttp import ClientSession, ClientTimeout
import markup
from database.database import Database

TOKEN = '6012383203:AAEtTX-jxszwteMinaKBE4vzOI15luSt2lM'
timeout = ClientTimeout(total=0)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
db = Database("database/database.db")
# Состояния ссылок
# states = {"Найдено": 1, "Не найдено": 0}


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Отправь мне ссылку на приложение в Google Play Store для проверки.", reply_markup=markup.main_markup)


# Обработчик текстовых сообщений (ссылок)
@dp.message_handler()
async def echo(message: types.Message):
    # Показ всех ссылок пользователя
    if message.text == "Мои ссылки":
        links = db.get_links_by_user(message.chat.id)
        if len(links) > 0:
            msg = ""
            for link in links:

                if link[3] == 1:
                    msg += f"{link[2]} - в сторе\n\n"
                else:
                    msg += f"{link[2]} - не в сторе\n\n"
            await bot.send_message(message.chat.id, msg)
        else:
            await bot.send_message(message.chat.id, "У вас нет добавленных ссылок!")
    # Удаление ссылок

    if message.text == "Удалить все ссылки":
        db.delete_all_links(message.chat.id)
        await bot.send_message(message.chat.id, "Удалил все ссылки!")
    # Проверяем, что сообщение содержит ссылку
    elif message.text.startswith('http'):
        # Получаем список ссылок для текущего пользователя или создаем новый, если его еще нет
        user_id = message.chat.id
        # user_link_list = user_links.get(user_id, [])
        # Добавляем новую ссылку в список
        db.add_link(user_id, message.text)
        # user_link_list.append(message.text)
        # user_links[user_id] = user_link_list
        await message.reply("Ссылка сохранена")
    else:
        await message.reply("Отправь мне ссылку на приложение в Google Play Store для проверки.")


async def scraper(user_id, state, link, session: ClientSession):
    async with session.get(link) as response:
        try:
            text = await response.text()
            if response.status == 200 and "Страница не найдена" not in text:
                if state == 0:
                    db.update_state_link(link, 1)
                    app_name = link.split("/details?id=")[-1]
                    await bot.send_message(user_id, f"{app_name} прошла модерку")
            else:
                if state == 1:
                    db.update_state_link(link, 0)
                    app_name = link.split("/details?id=")[-1]
                    await bot.send_message(user_id, f"Приложение {app_name} нет в сторе")
        except Exception as ex:
            print(ex)


async def check_links():
    while True:
        links = db.get_links()
        async with ClientSession(timeout=timeout) as session:
            tasks = []
            for user_id, link, state in links:
                tasks.append(asyncio.create_task(scraper(user_id=user_id, state=state, link=link, session=session)))
            await asyncio.gather(*tasks)
        await asyncio.sleep(10)


async def on_startup(_):
    asyncio.create_task(check_links())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)