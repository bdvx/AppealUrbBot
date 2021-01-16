import os
#from dotenv import load_dotenv
import webbrowser
import telebot
from telebot import types

# local setup
#load_dotenv('.env')

bot = telebot.TeleBot(os.environ.get('TG_TOKEN'));

catList = {}
catList[1] = {"Blago": "Благоустройство", "Soc": "Социальное направление"}
catList[2] = {"Opeka": "Опека", "Contacts": "Контакты"}
catList[3] = {"Alko": "Границы продажи алкогольной продукции"}

def makeCategories(catList):
    markup = types.InlineKeyboardMarkup()
    for key, value in catList.items():
        buttons = []
        for k, val in value.items():
                buttons.append(types.InlineKeyboardButton(text=val, callback_data=k))
                                            
        markup.add(*buttons)

    return markup


def makeSubCategories(category):
    markup = types.InlineKeyboardMarkup()
    for key, value in stringList.items():
        for k, val in value.items():
            markup.add(types.InlineKeyboardButton(text=val,
                                                callback_data="['value', '" + val + "', '" + k + "']"))

    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        subList = {}
        topText = "Выберите подкатегорию"
        if call.data == "Blago":
            subList[1] = {"Uborka": "Уборка", "Oborud": "Оборудование", "Transport": "Транспорт"}
            subList[2] = {"Zelen": "Зеленые насаждения", "Zamech": "Замечания от жителей"}
        if call.data == "Soc":
            subList[1] = {"Sport": "Спортивные мероприятия", "Semin": "Семинары, вебинары"}
            subList[2] = {"Prazd": "Праздничные мероприятия"}
            subList[3] = {"Trud": "Трудоустройство несовершеннолетних"}
        if call.data == "Opeka":
            topText += "\nПо иным вопросам Вы можете обратиться к сотруднику отдела опеки и попечительства по тел. 5282936"
            subList[1] = {"Sdelk": "Сделки", "Opek": "Опека"}
            subList[2] = {"Razresh": "Разрешение на трудоустройство несовершеннолетних"}
        if call.data == "Alko":
            webbrowser.open_new_tab("малаяохта.рф")
        if call.data == "Contacts":
            topText = "По всем интересующим вопросам Вы можете обратиться по тел. 5284663"
            subList[1] = {"Site": "Сайт МО", "VK": "Группа VK"}
            
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=topText, reply_markup=makeCategories(subList))



@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == "/new":
        bot.send_message(chat_id=message.from_user.id,
                     text="Выберите категорию:",
                     reply_markup=makeCategories(catList),
                     parse_mode='HTML')
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "/new - Новое обращение")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")



bot.polling(none_stop=True, interval=0) 