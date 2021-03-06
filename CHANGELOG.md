![ScheduleFlowBot](https://b.radikal.ru/b20/1910/3d/7268401b5e3c.png)
____
### ScheduleFlow changelog and history:
___  

__1.0B - 3 октября'19:__
- На основе ScheduleFlow начата разработка бота на платформе ВКонтакте.

__1.0.1B - 4 октября'19:__
- Небольшие дополнения. Повышение стабильности.

__1.2 - 5 октября'19:__  
- Добавлена функция crop_for_class, позволяющая искать класс в ограниченном диапазоне
- Сохранение расписания в папку (независимо от того, нужен отдельный класс или все)
- При использовании параметра 'all' в консоль выводятся номера классов

__1.2.1 - 6 октября'19:__
- Небольшие изменения, связаные, по большей части с ScheduleFlowBot

__1.1B - 6 октября'19:__
- Заложен функционал для реализации команд.
- Добавлена опция выбора даты.
- Повышена отказоустойчивость.

__1.3.4B - 9 октября'19:__
- Реализованы все функции
- Стабильная работа на сервере

__1.3 - 9 октября'19:__
- ScheduleFlowBot становится основой для дальнейшего развития

__1.4 - 10 октября'19:__
- UX 2.0. Работа осуществляется по большей части с помощью кнопок.

__1.4.5 - 10 октября'19:__
- Переделана функция, возвращающая дату
- Убраны баги
- Бот отправляет смайлики :) 

__1.4.6 - 14 октября'19:__
- Исправления багов

__1.4.7 - 17 октября'19:__
- Переделан внешний вид присылаемого расписания
- Добавлено расписание звонков
- Исправлен баг с множественным выбором класса
- Добавлен трекер состояния пользователя

__1.4.8 - 19 октября'19:__
- Минорные исправления
- Исправлено расписание звонков

__1.5 - 25 октября - ноябрь'19:__
- Расписание загружается на сервер прямо при нарезке
- Время отправки расписания снижено в несколько раз
- Снижен объем хранящихся данных засчет того, что хранятся только
  attachments и основное расписание (возможно отключить через параметр в
  Constantes)
- Бот "набирает сообщение"
- Если сообщение не является командой, бот ответит на него емким
  высказываением, либо просто прочитает
- Обработка стикеров, картинок, аудио
- Возможность отвечать через интерфейс консоли
- При запросе расширенной статистики отправляется гистограмма по
  пользователям
- Рассылка расписания пользователям одной командой
- Возможность включить и выключить "подписку" на расписание
- Небольшая утилита для работы с базой пользователей UserBase

__1.5.2 - 14 ноября'19:__
- Все переработано под работу с базой данных (шаблон опубликую позднее)
- Добавлено ведение статистики запросов и благодарностей пользователей
- Переработаны некоторые функции (например, удалить)
- Добавлена функция инфо
- Удалены датазависимые ответы из констант
- Писал под хардбасс, не уверен, что без него работать будет
- Добавлена обработка прочих событий

__1.6 - 20 ноября'19:__
- Вместо одной кнопки сделано 2: "на завтра" и "на сегодня" (с общим так же)
- Замена классов ошибкой

__1.7 - 1 декабря'19:__
- Переделана загрузка и нарезка расписания
- Загрузка общего расписания вместе с классами

__1.7.5 - 5 декабря'19:__
- Добавлен DialogFlow
- Бесконечные фиксы

__1.8 - 9 января'20:__
- Новое десятилетие - новая версия. Планировалась как SF 2.0, но было решено оставить нумерацию такой, какая есть (SF 1.8)
- **Полностью переписана кодовая база**
- Проект имеет многоуровневую иерархию
- Добавлено логгирование
- **Добавлена многопроцессная обработка**
- Парсинг сайта каждые 30 минут с уведомлениями о состоянии
- Авто-обновление расписания каждые 15 минут
- **Полностью переработан алгоритм нарезки расписания**
- Проверка расписания на сайте выполняется через POST-code
- Обработка дат с помощью dialogflow (например, "завтра" или "позавчера")
- **На расписании отображается дата и время обновления**
- **Дневник: пользователи могут добавлять домашнее задание и смотреть ДЗ, добавленное другими участниками**
- Расписание загружается на сервер только по запросу
- Переделана (создана) панель управления в консоли 
- Подтверждение рассылок в консоли