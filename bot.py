import os, requests
from dotenv import load_dotenv
import telebot
import string
import random
from telebot import types
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# local setup
#load_dotenv('.env')

bot = telebot.TeleBot(os.environ.get('TG_TOKEN'));

sender = os.environ.get('SENDER')
receivers = os.environ.get('RECEIVERS') #comma delimiter between recipients
sendCopyTo = os.environ.get('CC')
login = os.environ.get('LOGIN')
password = os.environ.get('PASSWORD')

newAppeal = '\nДля нового обращения напишите "новая заявка"'

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
subList["Opeka"][1] = {"Sdelk": "Сделки", "Opek": "Опека", "Inoe": "Иное"}
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


def processPhotoMessage(message):
    fileID = ''
    if message.photo:
        fileID = message.photo[-1].file_id
    elif message.document:
        if message.document.mime_type == "image/jpeg":
            fileID = message.document.file_id
        else:
            return "Not an image"
    print('fileID =', fileID)
    file_info = bot.get_file(fileID)
    print('file_info =', file_info)
    downloaded_file = bot.download_file(file_info.file_path)
    extension = file_info.file_path.rsplit('.', 1)[-1] # take last part after the dot
    return {"file": downloaded_file, "extension": extension}
    #with open("image.jpg", 'wb') as new_file:
    #    new_file.write(downloaded_file)
    #print 'file.file_path =', file.file_path

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
        subCategoryKey = data[3]
        categoryKey = data[1]
        subCategory = subList[data[1]][int(data[4])][subCategoryKey]
        category = catList[int(data[2])][categoryKey]
        if categoryKey == "Opeka":
            if subCategoryKey == "Inoe":
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="По иным вопросам обращайтесь в Местную администрацию МО Малая Охта по телефону 8 (812) 528-46-63" + newAppeal)
                return
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Раздел находится в работе. По данному вопросу обращайтесь в Местную администрацию МО малая Охта по телефону 8 (812) 528-46-63" + newAppeal)
                return
        elif categoryKey == "Soc":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="По данному вопросу обращайтесь в Местную администрацию МО Малая Охта по телефону 8 (812) 528-46-63" + newAppeal)
            return

        topText = "Укажите проблему"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=topText)
        bot.register_next_step_handler(call.message, problem_description, category, subCategory)


def problem_description(message, category, subCategory):
    try:
        msg = bot.reply_to(message, 'Укажите адрес')
        bot.register_next_step_handler(msg, problem_address, category, subCategory, message.text)

    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при отправке описания проблемы. Попробуйте отправить заявку заново.' + newAppeal)
        
def problem_address(message, category, subCategory, description):
    try:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Нет Фото')
        msg = bot.reply_to(message, 'Прошу Вас приложить фотографию(или несколько, не более 3-х), связанную с проблемой.', reply_markup=markup)
    
        bot.register_next_step_handler(msg, problem_photo, category, subCategory, description, message.text)

    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при отправке адреса. Попробуйте отправить заявку заново.' + newAppeal)

def problem_photo(message, category, subCategory, description, address, photoList = None):
    try:
        if message.photo != None or message.document != None:
            if photoList == None:
                photoList = []
            elif len(photoList) > 3:
                msg = bot.reply_to(message, 'Укажите Ваши контактные данные: имя, телефон или электронный адрес')
                bot.register_next_step_handler(msg, problem_solution, category, subCategory, description, address, photoList)
                return
            print("length", len(photoList))
            photo = processPhotoMessage(message)
            photoList.append(photo)
            msg = bot.reply_to(message, 'Прикрепите еще фото или укажите Ваши контактные данные: имя, телефон или электронный адрес')
            bot.register_next_step_handler(msg, problem_photo, category, subCategory, description, address, photoList)
            return
        if message.text == "Нет Фото":
            msg = bot.reply_to(message, 'Укажите Ваши контактные данные: имя, телефон или электронный адрес')
            bot.register_next_step_handler(msg, problem_solution, category, subCategory, description, address)
            return
        #if photo == "Not an image":
        #    bot.register_next_step_handler(message, problem_photo, category, subCategory, description)
        #    return
        if photoList != None:
            problem_solution(message, category, subCategory, description, address, photoList)
        else:
            msg = bot.reply_to(message, 'Укажите Ваши контактные данные: имя, телефон или электронный адрес')
            bot.register_next_step_handler(msg, problem_solution, category, subCategory, description, address, photoList)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при отправке фото. Попробуйте отправить заявку заново.' + newAppeal)


def problem_solution(message, category, subCategory, description, address, photoList = None):
    try:
        # Create a multipart message and set headers
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receivers
        msg["Subject"] = "Новая заявка"
        msg["Cc"] = sendCopyTo  # Recommended for mass emails

        body = """
        Категория: """ + category + """
        Подкатегория: """ + subCategory + """
        Описание проблемы: """ + description + """
        Адрес: """ + address + """
        Контактные данные: """ + message.text

        # Add body to email
        msg.attach(MIMEText(body, "plain"))
        if photoList != None:
            # photoList[0:3] because of the failing upload logic on previous step
            for photo in photoList[0:3]:
                photoPart = MIMEBase("application", "octet-stream")
                photoPart.set_payload(photo["file"])
                # Encode file in ASCII characters to send by email    
                encoders.encode_base64(photoPart)

                # Add header as key/value pair to attachment part
                photoPart.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {''.join(random.choices(string.ascii_uppercase + string.digits, k = 7))}.{photo['extension']}",
                )
                msg.attach(photoPart)
        try:
            #sslContext = ssl.create_default_context()
            #smtpObj = smtplib.SMTP_SSL("SMTP.Office365.com", 465, context = sslContext)
            smtpObj = smtplib.SMTP("smtp.office365.com", 587)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(login, password)
            smtpObj.sendmail(sender, receivers.split(","), msg.as_string())  
            print("Successfully sent email")
            smtpObj.quit()

            bot.send_message(message.from_user.id, "Ваше обращение принято. Если Вы указали контактные данные, с Вами свяжутся по данному вопросу." + newAppeal)
        except Exception as e:
            print("Error: unable to send email", e)
            bot.reply_to(message, 'Произошла ошибка при отправке заявки. Попробуйте отправить заявку заново.')
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при отправке заявки. Попробуйте отправить заявку заново.')



@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text.lower() == "новая заявка" or message.text == "/new":
        bot.send_message(chat_id=message.from_user.id,
                     text="Выберите категорию:",
                     reply_markup=makeCategories(catList, "categories"),
                     parse_mode='HTML')
    elif message.text == "помощь" or message.text == "/help":
        bot.send_message(message.from_user.id, 'Напишите "новая заявка" в чат для создания нового обращения')
    else:
        bot.send_message(message.from_user.id, 'Я Вас не понимаю. Для справки напишите "помощь" в чат')

bot.polling(none_stop=True, interval=0) 