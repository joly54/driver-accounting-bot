import telebot
import gspread
from gspread.cell import Cell
import json
from gspread_formatting import *
import time
from telebot import types
from datetime import datetime

adm = 800918003

gc = gspread.service_account(filename="key.json")
sh = gc.open("Cars")
wk = sh.sheet1
try:
    with open("drivers.json", "r") as file:
        drivers = json.load(file)
        print("Base founded")
except:
    drivers = []
labels = [
    "Дата",
    "Имя Фамилия",
    "Марка авто",
    "Гос.номер авто",
    "Дата время начало смены",
    "Дата время окончание смены",
    "Начальный киллометраж",
    "Конечный киллометраж",
    "Пробег авто за смену",
    "Количество заправленных литров",
    "Номер карты заправочной",
    "Сумма принятой налички",
    "Сумма заправки",
    "ЗП",
]


def update():
    try:
        t = str(int(time.time()))
        temp = sh.add_worksheet(title=t, rows=50, cols=20)
        sheets = sh.worksheets()
        for sheet in sheets:
            if sheet.title != t:
                sh.del_worksheet(sheet)

        for driver in drivers:
            cells = []
            formating = []
            sheet = sh.add_worksheet(title=driver["name"], rows=50, cols=20)
            for i in range(len(labels)):
                cells.append(Cell(row=1, col=i + 1, value=labels[i]))
            cells.append(Cell(row=2, col=1, value=driver["date"]))
            cells.append(Cell(row=2, col=2, value=driver["name"]))
            cells.append(Cell(row=2, col=3, value=driver["auto_n"]))
            cells.append(Cell(row=2, col=4, value=driver["auto_num"]))
            cells.append(Cell(row=2, col=5, value=driver["date_s"]))
            cells.append(Cell(row=2, col=6, value=driver["date_e"]))
            cells.append(Cell(row=2, col=7, value=driver["befor"]))
            cells.append(Cell(row=2, col=8, value=driver["after"]))
            cells.append(Cell(row=2, col=9, value=driver["after"] - driver["befor"]))
            cells.append(Cell(row=2, col=10, value=driver["liters"]))
            cells.append(Cell(row=2, col=11, value=driver["address"]))
            cells.append(Cell(row=2, col=12, value=driver["cash_g"]))
            cells.append(Cell(row=2, col=13, value=driver["cash_s"]))
            sheet.update_cells(cells)
            fmt = cellFormat(
                backgroundColor=color(0.53, 0.807, 0.98),
                textFormat=textFormat(bold=True),
                horizontalAlignment="CENTER",
            )
            formating.append((f"A1:M1", fmt))
            fmt = cellFormat(
                backgroundColor=color(1, 0.63, 0.47),
                textFormat=textFormat(bold=True),
                horizontalAlignment="CENTER",
            )
            formating.append((f"I1", fmt))
            formating.append((f"N1", fmt))
            fmt = cellFormat(horizontalAlignment="CENTER")
            formating.append((f"A2:M2", fmt))
            format_cell_ranges(sheet, formating)
            set_column_width(sheet, "A:M", 250)
        sh.del_worksheet(temp)
    except Exception as e:
        print(e)
        bot.send_message(adm, str(e))


def save():
    with open("drivers.json", "w") as file:
        json.dump(drivers, file)


bot = telebot.TeleBot(token)
mode = {}


@bot.message_handler(commands=["update"])
def update_command(message):
    try:
        user_id = message.from_user.id
        bot.send_message(user_id, "Обновление...")
        update()
        bot.send_message(user_id, "Обновлено")
    except Exception as e:
        print(e)
        bot.send_message(adm, str(e))


@bot.message_handler(commands=["edit"])
def update_command(message):
    try:
        user_id = message.from_user.id
        mode[user_id] = ["edit", -1]
        drivers_list = ""
        for i in range(len(drivers)):
            drivers_list += f"{i+1}) {drivers[i]['name']}\n"
        bot.send_message(
            user_id,
            "Выберите водителя котрого хотите редактировать(отправьте номер)\n"
            + drivers_list,
        )
        print(mode)
    except Exception as e:
        print(e)
        bot.send_message(adm, str(e))


@bot.message_handler(commands=["list"])
def update_command(message):
    try:
        user_id = message.from_user.id
        drivers_list = ""
        for i in range(len(drivers)):
            drivers_list += f"{i+1}) {drivers[i]['name']}\n"
        bot.send_message(user_id, "Доступные водители:\n\n" + drivers_list)
        print(mode)
    except Exception as e:
        print(e)
        bot.send_message(adm, str(e))


@bot.message_handler(commands=["delete"])
def update_command(message):
    try:
        user_id = message.from_user.id
        text = message.text
        text = text[text.find(" ") + 1 :]
        del drivers[int(text) - 1]
        save()
        bot.send_message(user_id, "Удалено")
        update()
        send_btns(user_id, "Обновлено")
    except Exception as e:
        print(e)
        bot.send_message(adm, str(e))


@bot.message_handler(commands=["add"])
def update_command(message):
    try:
        user_id = message.from_user.id
        mode[user_id] = ["add", len(drivers)]
        today = datetime.now()
        date = today.strftime("%d.%m.%Y")
        drivers.append(
            {
                "date": date,
                "name": "",
                "auto_n": "",
                "auto_num": "",
                "date_s": "",
                "date_e": "",
                "befor": 0,
                "after": 0,
                "liters": 0,
                "address": "",
                "cash_g": 0,
                "cash_s": 0,
                "status": 1,
            }
        )
        bot.send_message(user_id, "Отправьте имя водителя")
        print(mode)
    except Exception as e:
        print(e)
        bot.send_message(adm, str(e))


@bot.message_handler(commands=["exit"])
def update_command(message):
    try:
        user_id = message.from_user.id
        mode[user_id] = "waiting"
        send_btns(user_id, "Виберите функцию")
        print(mode)
    except Exception as e:
        print(e)
        bot.send_message(adm, str(e))


@bot.message_handler(commands=["run"])
def update_command(message):
    try:
        text = message.text
        text = text[text.find(" ") + 1 :]
        exec(text)
    except Exception as e:
        print(e)
        bot.send_message(adm, str(e))


def send_btns(user_id, text):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("/exit")
        button2 = types.KeyboardButton("/edit")
        button3 = types.KeyboardButton("/add")
        markup.add(button1, button2, button3)
        button1 = types.KeyboardButton("/update")
        button2 = types.KeyboardButton("/list")
        markup.add(button1, button2)
        bot.send_message(user_id, text=text, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(adm, str(e))


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    try:
        text = message.text
        user_id = message.from_user.id
        now = datetime.now()
        date_time = now.strftime("Time %H-%M-%S Date %d-%m-%y")
        date = now.strftime("%d-%m-%y")
        name = str(message.from_user.first_name)
        print(f"New message Name: {name}\tUser id:{user_id}\t{date_time}\tText: {text}")
        if user_id not in mode:
            send_btns(user_id, "Здраствуйте, выберите режим")
        else:
            if mode[user_id][0] == "add":
                ind = mode[user_id][1]
                if drivers[ind]["status"] == 1:
                    drivers[ind]["name"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(user_id, text="Отправьте модель машины")
                elif drivers[ind]["status"] == 2:
                    drivers[ind]["auto_n"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(user_id, text="Отправьте гос номер машины")
                elif drivers[ind]["status"] == 3:
                    drivers[ind]["auto_num"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id,
                        text="Отправьте время и дату начала смены в формате 07:00 21.09.2022",
                    )
                elif drivers[ind]["status"] == 4:
                    drivers[ind]["date_s"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id,
                        text="Отправьте время и дату окончания смены в формате 07:00 21.09.2022",
                    )
                elif drivers[ind]["status"] == 5:
                    drivers[ind]["date_e"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id, text="Отправьте начальный пробег(целое число)"
                    )
                elif not text.isdigit() and (
                    drivers[ind]["status"] == 6
                    or drivers[ind]["status"] == 7
                    or drivers[ind]["status"] == 8
                    or drivers[ind]["status"] == 10
                    or drivers[ind]["status"] == 11
                ):
                    bot.send_message(user_id, "Ошибка, отправьте целое число")
                elif drivers[ind]["status"] == 6:
                    drivers[ind]["befor"] = int(text)
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id, text="Отправьте конечний пробег(целое число)"
                    )
                elif drivers[ind]["status"] == 7:
                    drivers[ind]["after"] = int(text)
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id, text="Отправьте количесво заправленых листров"
                    )
                elif drivers[ind]["status"] == 8:
                    drivers[ind]["liters"] = int(text)
                    drivers[ind]["status"] += 1
                    bot.send_message(user_id, text="Отправьте номер карты заправочной")
                elif drivers[ind]["status"] == 9:
                    drivers[ind]["address"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id, text="Отправьте сумму принятой налички(целое число)"
                    )
                elif drivers[ind]["status"] == 10:
                    drivers[ind]["cash_g"] = int(text)
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id, text="Отправьте сумму заправки(целое число)"
                    )
                elif drivers[ind]["status"] == 11:
                    drivers[ind]["cash_s"] = int(text)
                    drivers[ind]["status"] += 1
                    save()
                    bot.send_message(user_id, text="Сохранено")
                    bot.send_message(user_id, text="Обновление таблицы")
                    update()
                    bot.send_message(user_id, text="Обновлено!")
            elif mode[user_id][0] == "edit":
                ind = mode[user_id][1]
                if mode[user_id][1] == -1:
                    mode[user_id][1] = int(text) - 1
                    ind = mode[user_id][1]
                    drivers[ind]["status"] = 1
                    bot.send_message(user_id, text="Отправьте новое имя водителя")
                elif drivers[ind]["status"] == 1:
                    drivers[ind]["name"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(user_id, text="Отправьте модель машины")
                elif drivers[ind]["status"] == 2:
                    drivers[ind]["auto_n"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(user_id, text="Отправьте гос номер машины")
                elif drivers[ind]["status"] == 3:
                    drivers[ind]["auto_num"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id,
                        text="Отправьте время и дату начала смены в формате 07:00 21.09.2022",
                    )
                elif drivers[ind]["status"] == 4:
                    drivers[ind]["date_s"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id,
                        text="Отправьте время и дату окончания смены в формате 07:00 21.09.2022",
                    )
                elif drivers[ind]["status"] == 5:
                    drivers[ind]["date_e"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id, text="Отправьте начальный пробег(целое число)"
                    )
                elif not text.isdigit() and (
                    drivers[ind]["status"] == 6
                    or drivers[ind]["status"] == 7
                    or drivers[ind]["status"] == 8
                    or drivers[ind]["status"] == 10
                    or drivers[ind]["status"] == 11
                ):
                    bot.send_message(user_id, "Ошибка, отправьте целое число")
                elif drivers[ind]["status"] == 6:
                    drivers[ind]["befor"] = int(text)
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id, text="Отправьте конечний пробег(целое число)"
                    )
                elif drivers[ind]["status"] == 7:
                    drivers[ind]["after"] = int(text)
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id, text="Отправьте количесво заправленых листров"
                    )
                elif drivers[ind]["status"] == 8:
                    drivers[ind]["liters"] = int(text)
                    drivers[ind]["status"] += 1
                    bot.send_message(user_id, text="Отправьте номер карты заправочной")
                elif drivers[ind]["status"] == 9:
                    drivers[ind]["address"] = text
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id, text="Отправьте сумму принятой налички(целое число)"
                    )
                elif drivers[ind]["status"] == 10:
                    drivers[ind]["cash_g"] = int(text)
                    drivers[ind]["status"] += 1
                    bot.send_message(
                        user_id, text="Отправьте сумму заправки(целое число)"
                    )
                elif drivers[ind]["status"] == 11:
                    drivers[ind]["cash_s"] = int(text)
                    drivers[ind]["status"] += 1
                    save()
                    bot.send_message(user_id, text="Сохранено")
                    bot.send_message(user_id, text="Обновление таблицы")
                    update()
                    bot.send_message(user_id, text="Обновлено!")
        save()
    except Exception as e:
        print(e)
        bot.send_message(adm, str(e))


bot.polling(none_stop=True, interval=0)
