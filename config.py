import pyodbc
from dotenv import load_dotenv
import os

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
