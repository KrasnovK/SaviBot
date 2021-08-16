import config


def users_in_table(user_id):
    command = f"SELECT user_id FROM [CensusDB].[dbo].[BotTableUsers] WHERE user_id = {user_id}"
    config.cursor.execute(command)
    records = config.cursor.fetchall()
    if len(records) != 0:
        return True
    return False


def double_form_id(form_id):
    command = f"SELECT form_id FROM [CensusDB].[dbo].[BotTable] WHERE form_id = {form_id}"
    config.cursor.execute(command)
    records = config.cursor.fetchall()
    if len(records) != 0:
        return True
    return False


def chek_form_id_from_user(form_id, user_id):
    command = f"SELECT form_id FROM [CensusDB].[dbo].[BotTable] WHERE form_id = {form_id} AND user_id = {user_id}"
    config.cursor.execute(command)
    records = config.cursor.fetchall()
    if len(records) != 0:
        return True
    return False
