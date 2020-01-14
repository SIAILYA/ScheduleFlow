import pendulum

from bot.Api import Vk, DialogFlow
from bot.database.DataBases import SettingsBase, UserBase, ScheduleBase, HomeworkBase
from bot.messages.user import Keyboard
from bot.messages.user.Answers import Answers
from bot.messages.user.Rings import GetRings
from bot.schedule.GetSchedule import GetSchedule, ScheduleInfo
from bot.stuff import Utilities
from bot.stuff.Logging import GetCustomLogger
from bot.stuff.Utilities import GetTodayDate, GetScheduleTomorrow, GetScheduleDate


class User:
    def __init__(self, event):
        self.req, self.grt, self.rec, self.hwc, self.hwa = False, False, False, False, False
        self.Vk = Vk()
        self.Users = UserBase()
        self.Settings = SettingsBase()
        self.Schedules = ScheduleBase()
        self.UserLogger = GetCustomLogger('UserLogger', f'userlogs/{event.obj.message["peer_id"]}')
        if not SettingsBase().GetSettings()['offline']:
            if event.obj.message['text']:
                self.Message(event)
            else:
                self.NoText(event)
        else:
            self.Vk.MessageSend(event.obj.message['peer_id'], Answers.OFFLINE)

        self.Users.IncreaseParameters(event.obj.message['peer_id'], requests=self.req, gratitudes=self.grt, received=self.rec, hw_check=self.hwc, hw_add=self.hwa)

    def NoText(self, event):
        pass

    def Message(self, event):
        user_id = event.obj.message['peer_id']
        message = event.obj.message['text']

        if message == 'raise':
            raise ValueError
        if message == 'beginning':
            self.Users.SetUserParameters(user_id, state=0)
            self.Vk.MessageSend(user_id, 'Главное меню', keyboard=Keyboard.MenuKeyboard())

        if (not self.Users.CheckUserInBase(user_id)) or (self.Users.GetUserState(user_id) in [1, 2]):
            self.UserRegister(event)
        elif self.Users.GetUserState(user_id) == -1:
            self.Users.SetUserParameters(user_id, state=0)
            self.Vk.MessageSend(user_id, 'Новая клавиатура, новые функции :)', keyboard=Keyboard.MenuKeyboard())
        elif self.Users.GetUserState(user_id) == 3:
            self.UserSettings(user_id, message)
        elif self.Users.GetUserState(user_id) == 4:
            user_info = self.Users.GetUserInfo(user_id)
            if message.lower() == 'показать дз':
                self.hwc = True
                self.UserLogger.info(f'Запрос на ДЗ')
                user_class = user_info["cls"]
                homework_date = user_info["homework_date"].replace("today", GetTodayDate())
                homework = HomeworkBase().GetHomework(homework_date, user_class)
                self.Vk.MessageSend(user_id, f'Домашнее задание {user_class} класса на {homework_date}:\n' + homework)
            elif message.lower() == 'добавить дз':
                self.UserLogger.info(f'Режим добавления ДЗ')
                self.Vk.MessageSend(user_id, 'Введи домашнее задание или нажми кнопку "Отмена"\nВнимание! Рядом с домашним заданием будет отображаться ссылка на твой профиль!', keyboard=Keyboard.DenyKeyboard())
                self.Users.SetUserParameters(user_id, state=6)
            elif message.lower() == 'указать дату':
                self.UserLogger.info(f'Режим выбора даты ДЗ')
                self.Vk.MessageSend(user_id, 'Введи дату, чтобы посмотреть домашнее задание')
                self.Users.SetUserParameters(user_id, state=5)
            elif message.lower() == 'пожаловаться':
                self.UserLogger.info(f'Отправлена жалоба на расписание')
                user_class = user_info["cls"]
                homework_date = user_info["homework_date"].replace("today", GetTodayDate())
                homework = HomeworkBase().GetHomework(homework_date, user_class)
                self.Vk.ConsoleMessage(f'Жалоба от @id{user_id}({user_info["name"]} {user_info["last"]}) на ДЗ {user_class} класса на {homework_date}:\n{homework}')
                self.Vk.MessageSend(user_id, 'Жалоба отправлена!')
            else:
                self.Users.SetUserParameters(user_id, state=0, hw_date='today')
                self.Vk.MessageSend(user_id, 'Главное меню', keyboard=Keyboard.MenuKeyboard())
        elif self.Users.GetUserState(user_id) == 5:
            date = DialogFlow().SendRequest(message)
            if 'system' in date:
                y, m, d = list(map(int, date.lstrip('system user_class').split('-')))
                hw_date = pendulum.date(y, m, d).__format__(Utilities.FORMAT)
                self.Users.SetUserParameters(user_id, state=4, hw_date=hw_date)
                self.Vk.MessageSend(user_id, f'Установлена дата {hw_date}')
            else:
                self.Users.SetUserParameters(user_id, state=4)
                self.Vk.MessageSend(user_id, 'Дата указана неверно!')
        elif self.Users.GetUserState(user_id) == 6:
            user_info = self.Users.GetUserInfo(user_id)
            lexics = DialogFlow().SendRequest(message)
            if lexics.lower() == 'мат':
                self.Vk.ConsoleMessage(f'@id{user_id}({user_info["name"]}) пытается добавить ДЗ:\n{message}')
                self.Vk.MessageSend(user_id, 'Возможно, домашнее задание содержит ненормативную лексику! Я не могу его добавить', keyboard=Keyboard.HomeworkKeyboard())
            else:
                if message.lower() != 'отмена':
                    self.hwa = True
                    self.UserLogger.info(f'Добавлено домашнее задание на {user_info["homework_date"].replace("today", GetTodayDate())}')
                    HomeworkBase().AddHomework(user_info["homework_date"].replace("today", GetTodayDate()), user_info["cls"], message + f' - (@id{user_id}({user_info["name"][0]}{user_info["last"][0]}))\n')
                    self.Vk.MessageSend(user_id, 'Домашнее задание добавлено!', keyboard=Keyboard.HomeworkKeyboard())
                    self.Vk.ConsoleMessage(f'@id{user_id}({user_info["name"]}) добавил ДЗ:\n{message}')
                else:
                    self.Vk.MessageSend(user_id, 'Окей, отмена', keyboard=Keyboard.HomeworkKeyboard())
            self.Users.SetUserParameters(user_id, state=4)
        elif self.Users.GetUserState(user_id) == 0:
            self.MainMenu(event)

    def MainMenu(self, event):
        user_id = event.obj.message['peer_id']
        message = event.obj.message['text']
        user_info = self.Users.GetUserInfo(user_id)
        if message.lower() == 'на сегодня':
            self.req = True
            self.UserLogger.info(f'Запрошено распсиание на сегодня')
            cls = user_info['cls']
            date = GetTodayDate()

            if ScheduleBase().GetReplace(date):
                cls = 'main'

            schedule = GetSchedule(date, cls)
            if schedule:
                self.rec = True
                self.UserLogger.info(f'Расписание отправлено')
                self.Vk.MessageSend(user_id, Answers.GIVE_TODAY, attachment=schedule)
            else:
                self.UserLogger.info(f'Расписание не отправлено')
                self.Vk.MessageSend(user_id, Answers.TODAY_NONE)
        elif message.lower() == 'на завтра':
            self.req = True
            self.UserLogger.info(f'Запрошено распсиание на завтра')
            cls = user_info['cls']
            date = GetScheduleTomorrow()

            if ScheduleBase().GetReplace(date):
                cls = 'main'
            schedule = GetSchedule(date, cls)
            if schedule:
                self.rec = True
                self.UserLogger.info(f'Расписание отправлено')
                if pendulum.today(tz=Utilities.TZ).weekday() == 5:
                    self.Vk.MessageSend(user_id, Answers.GIVE_MONDAY, attachment=schedule)
                else:
                    self.Vk.MessageSend(user_id, Answers.GIVE_TOMORROW, attachment=schedule)
            else:
                self.UserLogger.info(f'Расписание не отправлено')
                self.Vk.MessageSend(user_id, Answers.TOMORROW_NONE)
        elif message.lower() == 'общее на сегодня':
            self.req = True
            self.UserLogger.info(f'Запрошено общее распсиание на сегодня')
            cls = 'main'
            date = GetTodayDate()
            schedule = GetSchedule(date, cls)
            if schedule:
                self.rec = True
                self.UserLogger.info(f'Расписание отправлено')
                self.Vk.MessageSend(user_id, Answers.GIVE_TODAY, attachment=schedule)
            else:
                self.UserLogger.info(f'Расписание не отправлено')
                self.Vk.MessageSend(user_id, Answers.TODAY_NONE)
        elif message.lower() == 'общее на завтра':
            self.req = True
            self.UserLogger.info(f'Запрошено общее распсиание на завтра')
            cls = 'main'
            date = GetScheduleTomorrow()

            schedule = GetSchedule(date, cls)
            if schedule:
                self.rec = True
                self.UserLogger.info(f'Расписание отправлено')
                if pendulum.today(tz=Utilities.TZ).weekday() == 5:
                    self.Vk.MessageSend(user_id, Answers.GIVE_MONDAY, attachment=schedule)
                else:
                    self.Vk.MessageSend(user_id, Answers.GIVE_TOMORROW, attachment=schedule)
            else:
                self.UserLogger.info(f'Расписание не отправлено')
                self.Vk.MessageSend(user_id, Answers.TOMORROW_NONE)
        elif message.lower() == 'звонки':
            self.req = True
            self.rec = True
            self.UserLogger.info(f'Запрос звонков')
            self.Vk.MessageSend(user_id, message=f'Держи расписание звонков на {GetScheduleDate()}', attachment=GetRings(GetScheduleDate()))
        elif message.lower() == 'дз':
            self.UserLogger.info(f'Вход в дневник')
            if self.Settings.GetSettings()['diary']:
                self.Users.SetUserParameters(user_id, state=4)
                self.Vk.MessageSend(user_id, 'Дневник (?)', keyboard=Keyboard.HomeworkKeyboard())
            else:
                self.Vk.MessageSend(user_id, 'Прости, но дневник сейчас не работает 😥')
        elif message.lower() == 'настройки':
            self.UserLogger.info(f'Вход в настройки')
            self.Users.SetUserParameters(user_id, state=3)
            self.Vk.MessageSend(user_id, 'Меню настроек', keyboard=Keyboard.SettingsKeyboard(self.Users.GetUserInfo(user_id)['notifications'],
                                                                                             self.Users.GetUserInfo(user_id)['track_schedules']))
        elif message.lower()[:4] == 'инфо':
            info, date, cls = DialogFlow().SendRequest(message).split()
            date = Utilities.GetFormat(date)
            self.UserLogger.info(f'Запрошена информация о расписании на {date}')
            self.Vk.MessageSend(user_id, ScheduleInfo(date, cls))
        else:
            answer = DialogFlow().SendRequest(message)
            if 'system' in answer:
                self.req = True
                answer = answer.replace('today', GetTodayDate())
                cls, date = answer.upper().split()[1:]
                date = Utilities.GetFormat(date)
                if ScheduleBase().GetReplace(date):
                    cls = 'main'
                schedule = GetSchedule(date, cls.replace('ОБЩЕЕ', 'main').replace('USER_CLASS', user_info['cls']))
                self.UserLogger.info(f'Запрошено распсиание на {date}')
                if schedule:
                    self.rec = True
                    self.UserLogger.info(f'Расписание отправлено')
                    self.Vk.MessageSend(user_id, f'Держи расписание на {date}', attachment=schedule)
                else:
                    self.UserLogger.info(f'Распсиание не найдено')
                    self.Vk.MessageSend(user_id, f'Прости, но расписания на {date} нигде нет\nИспользуй команду "Инфо <дата>" для подробностей')
            elif 'homework' in answer:
                date = Utilities.GetFormat(answer.replace('today', GetTodayDate()).replace('homework ', ''))
                self.UserLogger.info(f'Запрошено ДЗ на {date}')
                self.Vk.MessageSend(user_id, f'Домашнее задание {user_info["cls"]} класса на {date}:\n' + HomeworkBase().GetHomework(date, user_info["cls"]))
            elif answer == 'мат':
                # TODO: Поработать над обработкой intents
                pass
            elif answer in 'Рад быть полезным 😉 Всегда к вашим услугам 🙂 Пожалуйста! Обращайся еще 🤗 С любовью, ScheduleFlow 🥰 Стараюсь для вас! 😀 Всегда пожалуйста 😉':
                self.grt = True
                self.Vk.MessageSend(user_id, answer)

    def UserRegister(self, event):
        user_id = event.obj.message['peer_id']
        message = event.obj.message['text']
        if not self.Users.CheckUserInBase(user_id):
            self.UserLogger.info('Новый юзер!')
            name, last = self.Vk.UserNameGet(user_id)
            self.Vk.MessageSend(user_id, f'Привет, {name}!\nДавай настроим бота под тебя. Для начала выбери класс',
                                keyboard=Keyboard.ChooseClassNum())
            self.Users.AddNewUser(user_id, name, last)
            self.Users.SetUserParameters(user_id, state=1)

        elif self.Users.GetUserState(user_id) == 1:
            if message in '567891011':
                self.UserLogger.info(f'Выбран {message} класс')
                self.Users.SetUserParameters(user_id, state=2, cls_num=int(message))
                class_num = self.Users.GetUserInfo(user_id)['cls_num']
                g_class = class_num in [5, 10, 11]
                self.Vk.MessageSend(user_id, f'Отлично! Теперь выбери букву класса', keyboard=Keyboard.ChooseClassLetter(g_class))

        elif self.Users.GetUserState(user_id) == 2:
            class_num = self.Users.GetUserInfo(user_id)['cls_num']
            g_class = class_num in [5, 10, 11]
            if ((message.lower() in 'абв') and (not g_class)) or ((message.lower() in 'абвг') and g_class):
                self.UserLogger.info(f'Установлен {class_num}{message} класс')
                self.Users.SetUserParameters(user_id, state=0, cls_lit=message)
                self.Vk.MessageSend(user_id, 'Замечательно! Ты всегда можешь изменить свой класс в настройках!', keyboard=Keyboard.MenuKeyboard())

    def UserSettings(self, user_id, message):
        if message.lower() == 'сменить класс':
            self.UserLogger.info('Запущена процедура смены класса')
            self.Users.SetUserParameters(user_id, state=1)
            self.Vk.MessageSend(user_id, 'Выбери номер класса', keyboard=Keyboard.ChooseClassNum())
        elif message.lower() == 'включить уведомления':
            self.UserLogger.info('Включены уведомления')
            self.Users.SetUserParameters(user_id, notifications=1)
            self.Vk.MessageSend(user_id, 'Уведомления включены!\nТеперь тебе будет приходить ежедневная рассылка расписания',
                                keyboard=Keyboard.SettingsKeyboard(self.Users.GetUserInfo(user_id)['notifications'],
                                                                   self.Users.GetUserInfo(user_id)['track_schedules']))
        elif message.lower() == 'выключить уведомления':
            self.UserLogger.info('Уведомления выключены')
            self.Users.SetUserParameters(user_id, notifications=0)
            self.Vk.MessageSend(user_id, 'Уведомления выключены!\nБольше ежедневная рассылка не потревожит тебя',
                                keyboard=Keyboard.SettingsKeyboard(self.Users.GetUserInfo(user_id)['notifications'],
                                                                   self.Users.GetUserInfo(user_id)['track_schedules']))
        elif message.lower() == 'отслеживать расписания':
            self.UserLogger.info('Включен трекинг расписания')
            self.Users.SetUserParameters(user_id, track_schedules=1)
            self.Vk.MessageSend(user_id, 'Включил отслеживание для тебя!\nТеперь каждые полчаса тебе будут приходить сообщения о состоянии расписаний на ближайшие дни!',
                                keyboard=Keyboard.SettingsKeyboard(self.Users.GetUserInfo(user_id)['notifications'],
                                                                   self.Users.GetUserInfo(user_id)['track_schedules']))
        elif message.lower() == 'не отслеживать расписания':
            self.UserLogger.info('Трекинг расписания отключен')
            self.Users.SetUserParameters(user_id, track_schedules=0)
            self.Vk.MessageSend(user_id,
                                'Отслеживание расписаний выключено! Можешь включить снова, если понадобится узнать статус расписаний, либо воспользуйся командой "Инфо <дата> <класс>"',
                                keyboard=Keyboard.SettingsKeyboard(self.Users.GetUserInfo(user_id)['notifications'],
                                                                   self.Users.GetUserInfo(user_id)['track_schedules']))
        elif message.lower() == 'назад':
            self.UserLogger.info('Выход из меню настроек')
            self.Users.SetUserParameters(user_id, state=0)
            self.Vk.MessageSend(user_id, 'Главное меню', keyboard=Keyboard.MenuKeyboard())