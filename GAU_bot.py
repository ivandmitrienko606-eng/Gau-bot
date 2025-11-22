from telebot import *

bot = telebot.TeleBot("8007821576:AAEFtW7FiEed89eE-F6ejLAVCeh2N7uFNUk", parse_mode=None)

name_room = []
info_room = {}
user_name = {}
invite_team = {}
teams = {}


def creat_new_id_room(name):
    new_id = len(info_room)
    info_room[new_id] = name
    return new_id

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать в GAU Report Bot\nСписок команд для руководителя:\n/addnewroom - создать новую команду\n/inviteteam - добавить сотрудника в команду\n/myteam - посмотреть команду и сотрудников")
    user = message.from_user
    if user.username not in user_name:
        user_name[user.username] = message.chat.id

@bot.message_handler(commands=['addnewroom'])
def new_room(message):
    bot.reply_to(message, "Придумайте имя для вашей комнаты:")
    bot.register_next_step_handler(message, process_room_name)

def process_room_name(message):
    name_room.append(message.text)
    room_id = creat_new_id_room(message.text)
    bot.reply_to(message, f"Ваша команда с именем: {message.text} зарегистрирована. Ваш id - {room_id}")
    teams[room_id] = []

@bot.message_handler(commands=['testsms'])
def receiving_sms(message):
    bot.reply_to(message, "Введите username пользователя (БЕЗ @), которому хотите отправить смс")
    bot.register_next_step_handler(message, send_username)
def send_username(message):
    username = message.text
    if username in user_name:
        bot.reply_to(message, "Пользователь найден. Напишите текст письма:")
        bot.register_next_step_handler(message, lambda m:  send_message(m, username))
    else:
        bot.reply_to(message, "Пользователь не зарегистрирован в нашем боте")
def send_message(message, username):
    bot.send_message(user_name[username], f"Вам письмецо от @{message.from_user.username}, ПИСЬМО: {message.text}")

@bot.message_handler(commands=['inviteteam'])
def request_username(message):
    bot.reply_to(message, "Введите username пользователя (БЕЗ @), которого хотите пригласить в команду")
    bot.register_next_step_handler(message, receiving_invite)

def receiving_invite(message):
    username = message.text
    if username in user_name:
        bot.reply_to(message, "Введите ID вашей команды")
        bot.register_next_step_handler(message, lambda m: save_invite(m, username))
    else:
        bot.reply_to(message, "Пользователь не зарегистрирован в нашем боте")
def save_invite(message, username):
    room_id = message.text

    if not room_id.isdigit() or int(room_id) not in teams:
        bot.reply_to(message, "Команды с таким ID не существует")
        return

    room_id = int(room_id)

    invite_team[username] = {
        "inviter": message.from_user.username,
        "room_id": room_id
    }

    bot.send_message(
        user_name[username],
        f"Вы приглашены в команду #{room_id} руководителя @{message.from_user.username}. "
        f"Напишите /accept_invite чтобы принять, или /reject_invite чтобы отклонить."
    )


@bot.message_handler(commands=['accept_invite'])
def accept_invite(message):
    username = message.from_user.username
    if username not in invite_team:
        bot.reply_to(message, "У вас нет приглашений в команду")
        return
    room_id = invite_team[username]["room_id"]
    teams[room_id].append(username)
    bot.reply_to(message, f"Вы успешно добавлены в команду #{room_id}!")
    del invite_team[username]

@bot.message_handler(commands=['reject_invite'])
def reject_invite(message):
    if message.from_user.username in invite_team:
        bot.reply_to(message, "Вы успешно отклонили приглашение")
        del invite_team[message.from_user.username]
    else:
        bot.reply_to(message, "У вас нет приглашений в команду")

@bot.message_handler(commands=['myteam'])
def my_team(message):
    bot.reply_to(message, "Введите id команды, сотрудников которой хотите посмотреть:")
    bot.register_next_step_handler(message, send_my_team)   # <<< ИСПРАВЛЕНО


def send_my_team(message):
    room_id = message.text

    if not room_id.isdigit():
        bot.reply_to(message, "ID должен быть числом")
        return

    room_id = int(room_id)

    if room_id not in teams:
        bot.reply_to(message, "Команды с таким ID не существует")
        return

    if len(teams[room_id]) == 0:
        bot.reply_to(message, f"В команде #{room_id} пока нет сотрудников.")
        return

    bot.reply_to(message, f"Участники команды #{room_id}:")
    for member in teams[room_id]:
        bot.send_message(message.chat.id, f"• @{member}")

bot.polling(none_stop=True)

