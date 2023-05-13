from vkbottle.bot import Bot, Message
from vkbottle import CtxStorage, BaseStateGroup
from dbcontroller import BotDB
import Keyboards
from timetableparser import update_excel_file
from timetableparser import get_data_from_excel

from config import *


class TimetableStates(BaseStateGroup):
    COURSE = 0
    GROUP = 1
    WEEK = 2
    END = 3


bot = Bot(token=token)
bot.labeler.vbml_ignore_case = True

ctx = CtxStorage()


def get_timetable(group: str, week_number: str, day: str) -> str:
    week_number = int(week_number)
    db = BotDB(database_path)

    answer = f"{week_number}-я неделя\n\n"

    days = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота') if day.lower() == 'все' else (day,)
    for weekday in days:
        answer += "\n\n" + "━" * 20 + "\n"
        answer += f"\U0001F4C5 {weekday.upper()}"
        rows = db.get_timetable(group, week_number, weekday)
        for row in rows:
            answer += "\n\n" + "\n".join((f"\U0001F565 {row['pairtime']}", f"\U0001F4DA {row['lesson']}"))

    return answer


async def update_timetable():
    await update_excel_file()

    timetable_data = get_data_from_excel(path_to_excel_ttb)

    bot_database = BotDB(database_path)
    bot_database.update_timetable(timetable_data)

    bot_database.close()


async def update_keyboards():
    bot_database = BotDB(database_path)
    Keyboards.courses_groups.clear()
    courses = tuple((row[0] for row in bot_database.get_courses()))
    new_buttons = Keyboards.create_onecmd_buttons(courses, cmd=Keyboards.courses_keyboard_cmd)
    Keyboards.courses_keyboard = Keyboards.TextKeyboard(*new_buttons).row().add_button(Keyboards.main_menu_button)

    for course in courses:
        groups = (row[0] for row in bot_database.get_groups(course))
        new_buttons = Keyboards.create_onecmd_buttons(groups, cmd=Keyboards.groups_keyboard_cmd)
        Keyboards.courses_groups[course] = Keyboards.TextKeyboard(*new_buttons)\
            .row().add_button(Keyboards.back_button)\
            .row().add_button(Keyboards.main_menu_button)


@bot.loop_wrapper.interval(hours=6)
async def update():
    await update_timetable()
    await update_keyboards()


@bot.on.private_message(payload={"command": "start"})
async def start(message: Message):
    answer = "Привет! Я бот-расписание ХТИ. Напиши в чат 'я застрял', чтобы вернуться в главное меню. " \
             "Давай начнем"
    await message.answer(answer)
    answer = "Выбери один из предложенных вариантов"
    keyboard = Keyboards.main_menu_keyboard
    await message.answer(message=answer, keyboard=keyboard)


@bot.on.private_message(text='я застрял')
@bot.on.private_message(payload={"cmd": "main menu"})
async def main_menu(message: Message):
    if await bot.state_dispenser.get(message.peer_id):
        await bot.state_dispenser.delete(message.peer_id)
    answer = "Выбери один из предложенных вариантов"
    keyboard = Keyboards.main_menu_keyboard
    await message.answer(message=answer, keyboard=keyboard)


# ----------------------------------------------------------------------------------------------------------------------

@bot.on.private_message(payload={"cmd": "Расписание"})
async def timetable(message: Message):
    await bot.state_dispenser.set(message.peer_id, TimetableStates.COURSE)
    answer = 'Выбери курс'
    keyboard = Keyboards.courses_keyboard

    await message.answer(message=answer, keyboard=keyboard)


@bot.on.private_message(state=TimetableStates.COURSE)
async def course_choosing(message: Message):
    if message.get_payload_json() is None:
        answer = 'Для навигации используй кнопки'
        await message.answer(message=answer)

    elif message.get_payload_json().get("cmd") == Keyboards.courses_keyboard_cmd:
        course = message.text
        ctx.set("course", course)
        await bot.state_dispenser.set(message.peer_id, TimetableStates.GROUP)

        answer = 'Выбери группу'
        keyboard = Keyboards.courses_groups[course]
        await message.answer(message=answer, keyboard=keyboard)


@bot.on.private_message(state=TimetableStates.GROUP)
async def group_choosing(message: Message):
    if message.get_payload_json() is None:
        answer = 'Для навигации используй кнопки'
        await message.answer(message=answer)

    elif message.get_payload_json().get("cmd") == Keyboards.groups_keyboard_cmd:
        group = message.text
        ctx.set("group", group)
        await bot.state_dispenser.set(message.peer_id, TimetableStates.WEEK)

        answer = 'Выбери неделю'
        keyboard = Keyboards.week_number_keyboard
        await message.answer(message=answer, keyboard=keyboard)

    elif message.get_payload_json().get("cmd") == "back":
        await bot.state_dispenser.set(message.peer_id, TimetableStates.COURSE)

        answer = 'Выбери курс, расписание которого хочешь посмотреть'
        keyboard = Keyboards.courses_keyboard
        await message.answer(message=answer, keyboard=keyboard)


@bot.on.private_message(state=TimetableStates.WEEK)
async def week_choosing(message: Message):
    if message.get_payload_json() is None:
        answer = 'Для навигации используй кнопки'
        await message.answer(message=answer)

    elif message.get_payload_json().get("cmd") == Keyboards.weeks_keyboard_cmd:
        week = message.text
        ctx.set("week", week)
        await bot.state_dispenser.set(message.peer_id, TimetableStates.END)

        answer = 'Выбери день недели'
        keyboard = Keyboards.weekday
        await message.answer(message=answer, keyboard=keyboard)
    elif message.get_payload_json().get("cmd") == "back":
        await bot.state_dispenser.set(message.peer_id, TimetableStates.GROUP)

        course = ctx.get("course")
        answer = 'Выбери группу, расписание которой хотите посмотреть'
        keyboard = Keyboards.courses_groups[course]
        await message.answer(message=answer, keyboard=keyboard)


@bot.on.private_message(state=TimetableStates.END)
async def day_choosing(message: Message):
    if message.get_payload_json() is None:
        answer = 'Для навигации используй кнопки'
        await message.answer(message=answer)

    elif message.get_payload_json().get("cmd") == Keyboards.days_keyboard_cmd:
        day = message.text

        answer = get_timetable(ctx.get("group"), ctx.get("week"), day)
        await message.answer(message=answer)
    elif message.get_payload_json().get("cmd") == "back":
        await bot.state_dispenser.set(message.peer_id, TimetableStates.WEEK)

        answer = 'Выбери неделю, расписание которой хочешь посмотреть'
        keyboard = Keyboards.week_number_keyboard
        await message.answer(message=answer, keyboard=keyboard)


# ----------------------------------------------------------------------------------------------------------------------

@bot.on.private_message(payload={'cmd': Keyboards.my_timetable_cmd})
async def my_timetable(message: Message):
    answer = "Этот раздел ещё в разработке"
    await message.answer(message=answer)


# ----------------------------------------------------------------------------------------------------------------------

@bot.on.private_message(payload={'cmd': Keyboards.settings_cmd})
async def settings(message: Message):
    answer = "Этот раздел ещё в разработке"
    await message.answer(message=answer)


bot.loop_wrapper.on_startup.append(update())
bot.run_forever()
