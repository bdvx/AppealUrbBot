import os
# from dotenv import load_dotenv
import telebot
from telebot import types

# load_dotenv('.env')

bot = telebot.TeleBot(os.environ.get('TG_TOKEN'));

stringList = {}
stringList[1] = {"Blago": "Благоустройство", "Soc": "Социальное направление"}
stringList[2] = {"Opeka": "Опека", "Contacts": "Контакты"}
stringList[3] = {"Alko": "Границы продажи алкогольной продукции"}

def makeCategories():
    markup = types.InlineKeyboardMarkup()
    for key, value in stringList.items():
        buttons = []
        for k, val in value.items():
                buttons.append(types.InlineKeyboardButton(text=val,
                                                    callback_data="['value', '" + k + "', '" + k + "']"))
                                            
        markup.add(*buttons)

    return markup


def makeSubCategories():
    markup = types.InlineKeyboardMarkup()
    for key, value in stringList.items():
        for k, val in value.items():
            markup.add(types.InlineKeyboardButton(text=val,
                                                callback_data="['value', '" + val + "', '" + k + "']"))

    return markup

@bot.message_handler(content_types=['text'])

def get_text_messages(message):

    if message.text == "Привет":
        bot.send_message(chat_id=message.from_user.id,
                     text="Выберите категорию:",
                     reply_markup=makeCategories(),
                     parse_mode='HTML')
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "/new - Новое обращение")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")



bot.polling(none_stop=True, interval=0) 