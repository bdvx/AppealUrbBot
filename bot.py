import os
from dotenv import load_dotenv
import telebot
from telebot import types
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# local setup
load_dotenv('.env')

bot = telebot.TeleBot(os.environ.get('TG_TOKEN'));

sender = os.environ.get('SENDER')
receivers = os.environ.get('RECEIVERS') #comma delimiter between recipients
CC = os.environ.get('CC')
login = os.environ.get('LOGIN')
password = os.environ.get('PASSWORD')

catList = {}
catList[1] = {"Blago": "Благоустройство", "Soc": "Социальное направление"}
catList[2] = {"Opeka": "Опека", "Contacts": "Контакты"}
catList[3] = {"Alko": "Границы продажи алкогольной продукции"}


subList = {}

subList["Blago"] = {}
subList["Blago"][1] = {"Uborka": "Уборка", "Oborud": "Оборудование", "Transport": "Транспорт"}
subList["Blago"][2] = {"Zelen": "Зеленые насаждения", "Inoe": "Иное"}

subList["Soc"] = {}
subList["Soc"][1] = {"Sport": "Спортивные мероприятия", "Semin": "Семинары, вебинары"}
subList["Soc"][2] = {"Prazd": "Праздничные мероприятия"}
subList["Soc"][3] = {"Trud": "Трудоустройство несовершеннолетних"}

subList["Opeka"] = {}
subList["Opeka"][1] = {"Sdelk": "Сделки", "Opek": "Опека"}
subList["Opeka"][2] = {"Razresh": "Разрешение на трудоустройство несовершеннолетних"}

subList["Contacts"] = {}
subList["Contacts"][1] = {"Site": "Сайт МО", "VK": "Группа VK"}

# URL buttons are hardcoded logic, maybe change if found ther way
def makeCategories(catList, catType):
    markup = types.InlineKeyboardMarkup()
    for key, value in catList.items():
        buttons = []
        for k, val in value.items():
            link = None
            if k == 'Alko' or k == 'Site':
                link = "http://малаяохта.рф/"
            elif k == 'VK':
                link = "https://vk.com/momoohta"
            buttons.append(types.InlineKeyboardButton(text=val, callback_data=f"{catType}:{k}:{key}", url=link))
                                            
        markup.add(*buttons)

    return markup


@bot.callback_query_handler(func=lambda call: call.data.split(':')[0].startswith('categories'))
def callback_inline(call):
    if call.message:
        
        topText = "Выберите подкатегорию"
        data = call.data.split(':')
        category = data[1]
        key = data[2]
        if category == "Opeka":
            topText += "\nПо иным вопросам Вы можете обратиться к сотруднику отдела опеки и попечительства по тел. 5282936"  
        elif category == "Contacts":
            topText = "По всем интересующим вопросам Вы можете обратиться по тел. 5284663"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=topText, reply_markup=makeCategories(subList[category], f"subCategories:{category}:{key}"))



@bot.callback_query_handler(func=lambda call: call.data.split(':')[0].startswith('subCategories'))
def callback_inline(call):
    if call.message:
        data = call.data.split(':')
        # here we get string with subCategories: category short name: number in category dict: subCat short name: number in subCat dict
        subCategory = subList[data[1]][int(data[4])][data[3]]
        category = catList[int(data[2])][data[1]]

        topText = "Прошу Вас описать проблему с указанием адреса, приложить фотографию и указать свои контактные данные для связи"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=topText)
        bot.register_next_step_handler(call.message, problem_description, category, subCategory)


def problem_description(message, category, subCategory):
    try:
        print(category, subCategory)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Нет Фото')
        msg = bot.reply_to(message, 'Прошу Вас приложить фотографию', reply_markup=markup)
        bot.register_next_step_handler(msg, problem_photo, category, subCategory, message.text)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при отправке описаия. Попробуйте отправить заявку заново.')



def problem_photo(message, category, subCategory, description):
    try:
        msg = bot.reply_to(message, 'Напишите Ваши предложения по выбранному направлению')
        bot.register_next_step_handler(msg, problem_solution, category, subCategory, description)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при отправке фото. Попробуйте отправить заявку заново.')




def problem_solution(message, category, subCategory, description):
    try:
        # Create a multipart message and set headers
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receivers
        msg["Subject"] = "Новая заявка"
        msg["Cc"] = CC  # Recommended for mass emails

        body = """
        Категория: """ + category + """
        Подкатегория: """ + subCategory + """
        Описание проблемы и контактные данные: """ + description + """
        Предложение по решению: """ + message.text

        # Add body to email
        msg.attach(MIMEText(body, "plain"))
        try:
            sslContext = ssl.create_default_context()
            smtpObj = smtplib.SMTP_SSL("smtp.gmail.com", 465, context = sslContext)
            smtpObj.login(login, password)
            smtpObj.sendmail(sender, receivers, msg.as_string())  
            print("Successfully sent email")
            smtpObj.close()
            bot.send_message(message.from_user.id, "Ваше обращение принято. Если вы указали контактные данные, с Вами свяжутся по данному вопросу.")
        except Exception:
            print("Error: unable to send email")
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при отправке предложений. Попробуйте отправить заявку заново.')



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