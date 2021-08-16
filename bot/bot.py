import logging
import pyodbc
from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Логирование
from sql import chek_form_id_from_user, double_form_id, users_in_table


load_dotenv()

# DB
SERVER = os.environ.get("SERVER")
DATABASE = os.environ.get("DATABASE")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
DRIVER = os.environ.get("DRIVER")

# TLG
TLG_TOKEN = os.environ.get("TLG_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# Connect to DB
cnxn = pyodbc.connect(
    f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}")
cursor = cnxn.cursor()

# Ответ бота
UNKNOWN_USER = "Вы должны получить доступ, напишите @konstantin_krasnov"

#SQL команды

INSERT_FORM_ID = "INSERT INTO [CensusDB].[dbo].[BotTable](user_id, username, full_name, form_id) VALUES "
DELETE_FORM_ID = "INSERT FROM [CensusDB].[dbo].[BotTable] WHERE form_id = "

MONTH = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}

logging.basicConfig(level=logging.INFO)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


async def start(message: types.Message):
    user = types.User.get_current()
    user_id = user.id
    full_name = user.full_name
    if users_in_table(user_id) is True:
        await message.answer(f"Привет, {full_name}\n\n"
                             f"Бот видит все сообщения\n"
                             f"Чтобы добавить анкету, просто введите id в чат\n"
                             f"Если id верное, вы получите сообщение, что анкета добавлена в базу\n"
                             f"Если в id ошибка, анкета не добавиться и нужно ввести верный id\n"
                             f"Если бот не реагирует на ваши действия, скорее всего он сломался, скажите об этом сразу "
                             f"@konstantin_krasnov\n\n"
                             f"Команды бота:\n"
                             f"/help - Подсказка\n"
                             f"/statistics - Показать статистику за месяц\n"
                             f"/del - Удалить анкету\n"
                             f"/cancel - Отменить действие\n\n"
                             f"P.S. Можете начинать вводить id, бот работает")
    else:
        await message.answer(UNKNOWN_USER)


class DelFormId(StatesGroup):
    waiting_delete_form_id = State()
    waiting_number_of_month = State()


async def statistics(message: types.Message):
    user = types.User.get_current()
    user_id = user.id
    if users_in_table(user_id) is True:
        await message.answer("Введите номер месяца, чтобы посмотреть статистику")
        await DelFormId.waiting_number_of_month.set()
    else:
        await message.answer(UNKNOWN_USER)


async def statistics_chosen(message: types.Message, state: FSMContext):
    user = types.User.get_current()
    user_id = user.id
    full_name = user.full_name
    month_number = message.text
    if not month_number.isdigit() or not 1 <= int(month_number) <= 12:
        await message.answer(f"Это что за месяц такой?\n"
                             f"Нажмите /statistics и попробуйте еще раз")
        await state.reset_data()
        await state.finish()
    elif message.from_user.id == ADMIN_ID:
        command_admin = f"SELECT [full_name], COUNT(*) AS [Кол-во анкет] " \
                        f"FROM [CensusDB].[dbo].[BotTable] " \
                        f"WHERE month(date) = {int(month_number)} " \
                        f"and year(date) = year(GETDATE()) " \
                        f"GROUP BY [full_name]"
        cursor.execute(command_admin)
        records = cursor.fetchall()
        for row in records:
            await message.answer(f"Месяц: {MONTH[int(month_number)]}\n"
                                 f"{row[0]}\n"
                                 f"Кол-во анкет: {row[1]}\n\n")
        await message.answer(f"/statistics\n"
                             f"/cancel")
        await state.reset_data()
        await state.finish()
    else:
        command = f"SELECT count(*) AS [Кол-во анкет] " \
                  f"FROM [CensusDB].[dbo].[BotTable] " \
                  f"WHERE user_id = {user_id} " \
                  f"AND month(date) = {int(month_number)} " \
                  f"AND year(date) = year(GETDATE())"
        cursor.execute(command)
        records = cursor.fetchone()
        await state.reset_data()
        await state.finish()
        await message.answer(f"Статистика:\n"
                             f"{full_name}\n"
                             f"Месяц: {MONTH[int(month_number)]}\n"
                             f"Кол-во анкет: {records[0]}\n\n"
                             f"Чтобы посмотреть статистику за другой месяц, "
                             f"нажмите /statistics\n"
                             f"Для отмены нажмите /cancel\n")


async def delete(message: types.Message):
    user = types.User.get_current()
    user_id = user.id
    if users_in_table(user_id) is True:
        await message.answer("Введите id анкеты, которую хотите удалить")
        await DelFormId.waiting_delete_form_id.set()
    else:
        await message.answer(UNKNOWN_USER)


async def form_id_delete_chosen(message: types.Message, state: FSMContext):
    user = types.User.get_current()
    user_id = user.id
    form_id = message.text
    if chek_form_id_from_user(form_id, user_id) is not True:
        await message.answer("Кажется, это не ваша анкета\n"
                             "Нажмите /del и введите корректное id\n"
                             "Для отмены нажмите /cancel")
        await state.reset_data()
        await state.finish()
    else:
        command = f"DELETE FROM [CensusDB].[dbo].[BotTable] " \
                  f"WHERE [form_id] = {form_id} AND [user_id] = {user_id}"
        cursor.execute(command)
        cnxn.commit()
        await state.reset_data()
        await state.finish()
        await message.answer(f"Анкета {form_id} успешно удалена\n"
                             f"Введите id или команду")


async def cmd_cancel(message: types.Message, state: FSMContext):
    user = types.User.get_current()
    user_id = user.id
    if users_in_table(user_id) is True:
        await state.reset_data()
        await state.finish()
        await message.answer("Действие отменено\n"
                             "Введите id или команду")
    else:
        await message.answer(UNKNOWN_USER)


async def echo(message):
    user = types.User.get_current()
    user_id = user.id
    form_id = message.text
    if users_in_table(user_id) is not True:
        await message.answer(UNKNOWN_USER)
    else:
        if not form_id.isdigit():
            await message.answer(f"Что за буквы в id? Ну ёмаё\n"
                                 f"Введите корректное id или команду")
        else:
            if double_form_id(form_id) is not False:
                await message.answer(f"id {form_id} уже есть в базе\n"
                                     f"Введите корректный id")
            else:
                username = user.username
                full_name = user.full_name
                if 194342 < int(form_id) <= 999999:
                    command = f"{INSERT_FORM_ID} " \
                              f"({user_id}, '{username}', '{full_name}', {form_id})"
                    cursor.execute(command)
                    cnxn.commit()
                    await message.answer(f"{form_id} добавлена в базу\n"
                                         f"Введите следующее id или команду")
                else:
                    await message.answer(f"Неправильный id анкеты\n"
                                         f"Введите корректное id или команду")


# for Selectel
async def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start", "help"])
    dp.register_message_handler(statistics, commands="statistics")
    dp.register_message_handler(statistics_chosen, state=DelFormId.waiting_number_of_month)
    dp.register_message_handler(delete, commands="del")
    dp.register_message_handler(form_id_delete_chosen, state=DelFormId.waiting_delete_form_id)
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(echo)


async def process_event(update, dp: Dispatcher):
    Bot.set_current(dp.bot)
    await dp.process_update(update)


# for Selectel serverless entry point
async def main(**kwargs):
    bot = Bot(token=TLG_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    await register_handlers(dp)

    update = types.Update.to_object(kwargs)
    await process_event(update, dp)

    return "ok"

