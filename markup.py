from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton


main_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn_my_links = KeyboardButton("Мои ссылки")
btn_delete_links = KeyboardButton("Удалить все ссылки")
main_markup.add(btn_my_links, btn_delete_links)