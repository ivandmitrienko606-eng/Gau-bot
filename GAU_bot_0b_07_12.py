from telebot import *
import datetime

bot = telebot.TeleBot("8007821576:AAEFtW7FiEed89eE-F6ejLAVCeh2N7uFNUk", parse_mode=None)

class Register_User:
    def __init__(self, storage):
        self.bot = bot
        self.storage = storage
        self.register_handlers()
    def register_handlers(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.bot.reply_to(message,
                         "Добро пожаловать в GAU Report Bot\n"
                         "Список команд для руководителя:\n"
                         "/addnewroom - создать новую команду\n"
                         "/inviteteam - добавить сотрудника в команду\n"
                         "/myteam - посмотреть команду и сотрудников")
            user = message.from_user
            if user.username not in self.storage.user_name:
                self.storage.user_name[user.username] = message.chat.id
class BotStorage:
    def __init__(self):
        self.info_room = {}
        self.user_name = {}
        self.invite_team = {}
        self.teams = {}
        self.tasks = {}

class Team:
    def __init__(self, storage):
        self.bot = bot
        self.storage = storage
        self.register_handlers()
    def register_handlers(self):
        @self.bot.message_handler(commands=['addnewroom'])
        def new_room(message):
            self.bot.reply_to(message, "Придумайте имя для вашей комнаты:")
            self.bot.register_next_step_handler(message, self.process_room_name)

        @self.bot.message_handler(commands=['myteam'])
        def my_team(message):
            self.bot.reply_to(message, "Введите id команды, сотрудников которой хотите посмотреть:")
            self.bot.register_next_step_handler(message, self.send_my_team)

    def process_room_name(self, message):
        name = message.text
        room_id = self.create_new_id_room()
        self.bot.reply_to(message, f"Ваша команда с именем: {name} зарегистрирована. Ваш id - {room_id}")
        self.storage.teams[room_id] = []
        self.storage.info_room[room_id] = {
            "name": name,
            "leader": message.from_user.username
        }

    def create_new_id_room(self):
        new_id = len(self.storage.info_room)
        return new_id

    def send_my_team(self, message):
        room_id = message.text
        if not room_id.isdigit():
            self.bot.reply_to(message, "ID должен быть числом")
            return
        room_id = int(room_id)
        if room_id not in self.storage.teams:
            self.bot.reply_to(message, "Команды с таким ID не существует")
            return
        if message.from_user.username not in self.storage.teams[room_id]:
            if (self.storage.info_room[room_id]['leader'] != message.from_user.username):
                self.bot.reply_to(message, "Вы не состоите в данной команде и не можете просматривать её сотрудников")
                return
        room_info = self.storage.info_room[room_id]
        members = self.storage.teams[room_id]
        members_text = "\n".join(f"• @{member}" for member in members)
        text = (
            f"Команда: {room_info['name']}\n"
            f"Руководитель: @{room_info['leader']}\n"
            f"Участники команды:\n{members_text if members_text else '—'}"
        )
        self.bot.send_message(message.chat.id, text)

class Add_Worker:
    def __init__(self, storage):
        self.bot = bot
        self.storage = storage
        self.register_handlers()

    def register_handlers(self):
        @self.bot.message_handler(commands=['inviteteam'])
        def request_username(message):
            self.bot.reply_to(message, "Введите username пользователя (БЕЗ @), которого хотите пригласить в команду")
            self.bot.register_next_step_handler(message, self.receiving_invite)

        @self.bot.message_handler(commands=['accept_invite'])
        def accept_invite(message):
            username = message.from_user.username
            if username not in self.storage.invite_team:
                self.bot.reply_to(message, "У вас нет приглашений в команду")
                return
            room_id = self.storage.invite_team[username]["room_id"]
            self.storage.teams[room_id].append(username)
            self.bot.reply_to(message, f"Вы успешно добавлены в команду #{room_id}!")
            del self.storage.invite_team[username]

        @self.bot.message_handler(commands=['reject_invite'])
        def reject_invite(message):
            if message.from_user.username in self.storage.invite_team:
                self.bot.reply_to(message, "Вы успешно отклонили приглашение")
                del self.storage.invite_team[message.from_user.username]
            else:
                self.bot.reply_to(message, "У вас нет приглашений в команду")

    def receiving_invite(self, message):
        username = message.text
        if username in self.storage.user_name:
            self.bot.reply_to(message, "Введите ID вашей команды")
            self.bot.register_next_step_handler(message, lambda m: self.save_invite(m, username))
        else:
            self.bot.reply_to(message, "Пользователь не зарегистрирован в нашем боте")

    def save_invite(self, message, username):
        room_id = message.text
        if not room_id.isdigit() or int(room_id) not in self.storage.teams:
            self.bot.reply_to(message, "Команды с таким ID не существует")
            return
        room_id = int(room_id)
        if self.storage.info_room[room_id]['leader'] != message.from_user.username:
            self.bot.reply_to(message, "ATTENTION!!!\n"
                                       "Вы не являетесь руководителем данной команды!\n"
                                       "Вы не сможете пригласить в неё сотрудника!!!")
            return
        self.storage.invite_team[username] = {
            "inviter": message.from_user.username,
            "room_id": room_id
        }
        self.bot.send_message(
            self.storage.user_name[username],
            f"Вы приглашены в команду #{room_id} руководителя @{message.from_user.username}. "
            f"Напишите /accept_invite чтобы принять, или /reject_invite чтобы отклонить."
        )
        self.bot.reply_to(message, f"Приглашение {username} успешно отправлено!")
class Create_Task:
    def __init__(self, storage):
        self.bot = bot
        self.storage = storage
        self.register_handlers()
    def register_handlers(self):
        @self.bot.message_handler(commands=['add_task'])
        def add_task(message):
            self.bot.reply_to(message, "Введите id команды, сотруднику которой вы хотите выдать задание:")
            self.bot.register_next_step_handler(message, self.task_team)
    def task_team(self, message):
        room_id = message.text
        if not room_id.isdigit() or int(room_id) not in self.storage.teams:
            self.bot.reply_to(message, "Команды с таким ID не существует")
            return
        room_id = int(room_id)
        if message.from_user.username != self.storage.info_room[room_id]['leader']:
            self.bot.reply_to(message, "Вы не можете выдавать задачи в этой команде, т.к. не являетесь её лидером")
            return
        members = self.storage.teams[room_id]
        members_text = "\n".join(f"• @{member}" for member in members)
        text = (
            f"Участники вашей команды:\n{members_text if members_text else '—'}"
        )
        self.bot.send_message(message.chat.id, text)
        self.bot.reply_to(message, "Введите username пользователя (БЕЗ @), котому хотите выдать задачу")
        self.bot.register_next_step_handler(message, lambda m: self.create_task(m, room_id))
    def create_task(self, message, room_id):
        username = message.text
        if username not in self.storage.teams[room_id]:
            self.bot.reply_to(message, "Сотрудник с таким username не находится в вашей команде")
            return
        self.bot.reply_to(message, f"Составьте задачу для @{username}")
        self.bot.register_next_step_handler(message, lambda m: self.save_task(m, room_id, username))
    def save_task(self, message, room_id, username):
        task = message.text
        task_obj = {
            "room_id": room_id,
            "leader": message.from_user.username,
            "task": task,
            "time": datetime.datetime.now().timestamp(),
            "file_id": None
        }
        if username not in self.storage.tasks:
            self.storage.tasks[username] = []
        self.storage.tasks[username].append(task_obj)
        self.bot.reply_to(message, f"Текст задачи для @{username} успешно сохранён! \n Прикрепите файл или отправьте /skip для отправки задачи сотруднику.")
        self.bot.register_next_step_handler(message, lambda m: self.add_file_to_task(m, room_id, username))

    def add_file_to_task(self, message, room_id, username):
        if message.text == "/skip":
            self.send_task(username, room_id)
            self.bot.reply_to(message, f"Задача сотруднику @{username} успешно отправлена!")
            return
        if message.content_type == "document":
            file_id = message.document.file_id
            self.storage.tasks[username][-1]["file_id"] = file_id
            self.send_task(username, room_id)
            self.bot.reply_to(message, f"Задача сотруднику @{username} успешно отправлена!")
        else:
            self.bot.reply_to(message, "Пожалуйста, прикрепите файл или отправьте /skip для пропуска.")
            self.bot.register_next_step_handler(message, lambda m: self.add_file_to_task(m, room_id, username))

    def send_task(self, username, room_id):
        task_info = self.storage.tasks[username][-1]
        text = f"У вас новая задача из команды: {self.storage.info_room[room_id]['name']} руководителя @{task_info['leader']}.\n{task_info['task']}"
        self.bot.send_message(self.storage.user_name[username], text)
        if task_info["file_id"]:
            self.bot.send_document(self.storage.user_name[username], task_info["file_id"])

class View_Task:
    def __init__(self, storage):
        self.bot = bot
        self.storage = storage
        self.register_handlers()

    def register_handlers(self):
        @self.bot.message_handler(commands=['my_task'])
        def my_tasks(message):
            username = message.from_user.username
            if username not in self.storage.tasks or len(self.storage.tasks[username]) == 0:
                self.bot.reply_to(message, "У вас нет задач на данный момент.")
                return
            tasks = self.storage.tasks[username]
            text_lines = []
            for i, task in enumerate(tasks, start=1):
                # Преобразуем timestamp в нормальное время
                time_str = datetime.datetime.fromtimestamp(task['time']).strftime("%d.%m.%Y %H:%M:%S")
                text_lines.append(
                    f"📌 Задача #{i}\n"
                    f"Команда: {task['room_id']}\n"
                    f"От руководителя: @{task['leader']}\n"
                    f"Когда выдана: {time_str}\n"
                    f"Текст: {task['task']}\n"
                    f"Файл: {'Есть' if task['file_id'] else 'Нет'}\n"
                )
            final_text = "\n".join(text_lines)
            self.bot.send_message(message.chat.id, final_text)

        @self.bot.message_handler(commands=['view_task'])
        def number_task(message):
            self.bot.reply_to(message, "Введите номер задачи которую хотите посмотреть")
            self.bot.register_next_step_handler(message, self.view_task)

    def view_task(self, message):
        username = message.from_user.username
        if username not in self.storage.tasks or len(self.storage.tasks[username]) == 0:
            self.bot.reply_to(message, "У вас нет задач на данный момент.")
            return
        tasks = self.storage.tasks[username]
        number_task = message.text
        if not number_task.isdigit() or int(number_task) < 1 or int(number_task) > len(tasks):
            self.bot.reply_to(message, "У вас нет задачи с таким номером.")
            return
        number_task = int(number_task)
        info_task = self.storage.tasks[username][number_task - 1]
        time_str = datetime.datetime.fromtimestamp(info_task['time']).strftime("%d.%m.%Y %H:%M:%S")
        text_lines = []
        text_lines.append(
            f"📌 Задача #{number_task}\n"
            f"Команда: {info_task['room_id']}\n"
            f"От руководителя: @{info_task['leader']}\n"
            f"Когда выдана: {time_str}\n"
            f"Текст: {info_task['task']}\n"
            f"Файл: {'Отсутствует' if info_task['file_id'] is None else 'Прикреплён' } \n"
        )
        final_text = "\n".join(text_lines)
        self.bot.send_message(message.chat.id, final_text)
        if info_task["file_id"]:
            self.bot.send_document(message.chat.id, info_task["file_id"])
storage = BotStorage()
register_user = Register_User(storage)
team = Team(storage)
add_worker = Add_Worker(storage)
create_task = Create_Task(storage)
view_task = View_Task(storage)

bot.polling(none_stop=True)

