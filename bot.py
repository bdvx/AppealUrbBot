import os
from dotenv import load_dotenv
import smtplib
import webbrowser
import telebot
from telebot import types

# local setup
load_dotenv('.env')

bot = telebot.TeleBot(os.environ.get('TG_TOKEN'));

sender = os.environ.get('SENDER')
receivers = os.environ.get('RECEIVERS').split(',')
login = os.environ.get('LOGIN')
password = os.environ.get('PASSWORD')

catList = {}
catList[1] = {"Blago": "Благоустройство", "Soc": "Социальное направление"}
catList[2] = {"Opeka": "Опека", "Contacts": "Контакты"}
catList[3] = {"Alko": "Границы продажи алкогольной продукции"}

def makeCategories(catList, catType):
    markup = types.InlineKeyboardMarkup()
    for key, value in catList.items():
        buttons = []
        for k, val in value.items():
            buttons.append(types.InlineKeyboardButton(text=val, callback_data=f"{k}:{catType}"))
                                            
        markup.add(*buttons)

    return markup


def makeSubCategories(category):
    markup = types.InlineKeyboardMarkup()
    for key, value in stringList.items():
        for k, val in value.items():
            markup.add(types.InlineKeyboardButton(text=val,
                                                callback_data="['value', '" + val + "', '" + k + "']"))

    return markup


@bot.callback_query_handler(func=lambda call: call.data.split(':')[1].startswith('categories'))
def callback_inline(call):
    if call.message:
        subList = {}
        topText = "Выберите подкатегорию"
        value = call.data.split(':')[0]
        if value == "Blago":
            topText = call.message
            subList[1] = {"Uborka": "Уборка", "Oborud": "Оборудование", "Transport": "Транспорт"}
            subList[2] = {"Zelen": "Зеленые насаждения", "Zamech": "Замечания от жителей"}
        if value == "Soc":
            subList[1] = {"Sport": "Спортивные мероприятия", "Semin": "Семинары, вебинары"}
            subList[2] = {"Prazd": "Праздничные мероприятия"}
            subList[3] = {"Trud": "Трудоустройство несовершеннолетних"}
        if value == "Opeka":
            topText += "\nПо иным вопросам Вы можете обратиться к сотруднику отдела опеки и попечительства по тел. 5282936"
            subList[1] = {"Sdelk": "Сделки", "Opek": "Опека"}
            subList[2] = {"Razresh": "Разрешение на трудоустройство несовершеннолетних"}
        if value == "Alko":
            webbrowser.open_new_tab("http://малаяохта.рф/")
        if value == "Contacts":
            topText = "По всем интересующим вопросам Вы можете обратиться по тел. 5284663"
            subList[1] = {"Site": "Сайт МО", "VK": "Группа VK"}
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=topText, reply_markup=makeCategories(subList, f"subCategories:{value}"))


@bot.callback_query_handler(func=lambda call: call.data.split(':')[1].startswith('subCategories'))
def callback_inline(call):
    if call.message:
        subList = {}
        data = call.data.split(':')
        subCategory = data[0]
        category = data[1]
        if subCategory == "Site":
            webbrowser.open_new_tab("http://малаяохта.рф/")
        elif subCategory == "Uborka":

            message = """Subject: SMTP e-mail test

            This is a test e-mail message.
            """
        
            try:
                smtpObj = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                smtpObj.login(login, password)
                smtpObj.sendmail(sender, receivers, message)  
                print("Successfully sent email")
                smtpObj.close()
            except Exception:
                print("Error: unable to send email")
        elif subCategory == "VK":
            webbrowser.open_new_tab("https://vk.com/momoohta")
        else:
            topText = "Прошу Вас описать проблему с указанием адреса, приложить фотографию и указать свои контактные данные для связи"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=topText)



@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == "/new":
        bot.send_message(chat_id=message.from_user.id,
                     text="Выберите категорию:",
                     reply_markup=makeCategories(catList, "categories"),
                     parse_mode='HTML')
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "/new - Новое обращение")
    else:
        bot.send_message(message.from_user.id, "Я Вас не понимаю. Для справки напишите /help.")



bot.polling(none_stop=True, interval=0) 