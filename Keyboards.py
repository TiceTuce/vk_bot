from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback
from typing import Iterable


class Button:

    def __init__(self, label: str, payload: dict[str, int | str]):
        self.label = label
        self.payload = payload


class TextKeyboard(Keyboard):

    def __init__(self, *buttons: Button, one_time=False):
        super().__init__(one_time=one_time)

        for number, button in enumerate(buttons, start=1):
            if number % 5 == 0:
                self.row()
            self.add_button(button)

    def get_payload(self) -> tuple:
        result = []

        rows = self.buttons
        for row in rows:
            for button in row:
                button_payload: dict = button.action.get_data().get('payload')
                result.append(button_payload)

        return tuple(result)

    def get_cmds(self) -> tuple:
        payload = self.get_payload()

        return tuple(map(lambda element: element.get('cmd'), payload))

    def add_button(self, button: Button):
        self.add(Text(label=button.label, payload=button.payload))

        return self

    def add_back_button(self):
        self.row().add_button(back_button)

    def add_main_button(self):
        self.row().add_button(main_menu_button)


def create_onecmd_buttons(labels: Iterable, cmd='') -> tuple:
    return tuple(Button(label=label, payload={"cmd": cmd}) for label in labels)


courses_keyboard_cmd = "course has chosen"
groups_keyboard_cmd = "group was chosen"
weeks_keyboard_cmd = "week was chosen"
days_keyboard_cmd = "day was chosen"
main_menu_cmd = "main menu"
back_cmd = "back"
my_timetable_cmd = "мое расписание"
settings_cmd = 'настройки'

main_menu_button = Button(label="В главное меню", payload={"cmd": main_menu_cmd})
back_button = Button(label="Назад", payload={"cmd": back_cmd})

main_menu_keyboard = TextKeyboard(
    Button(label='Расписание', payload={'cmd': 'Расписание'})
).row().add_button(
    Button(label='Мое расписание', payload={'cmd': my_timetable_cmd})
).row().add_button(
    Button(label="Настроить группу", payload={"cmd": settings_cmd})
)

courses_keyboard = TextKeyboard(
    Button(label="1 курс", payload={"cmd": courses_keyboard_cmd}),
    Button(label="2 курс", payload={"cmd": courses_keyboard_cmd}),
    Button(label="3 курс", payload={"cmd": courses_keyboard_cmd}),
    Button(label="4, 5, 6 курс", payload={"cmd": courses_keyboard_cmd})
).row().add_button(main_menu_button)

first_course_groups_keyboard = TextKeyboard(
    Button(label="12-1(ХЭн 22-01)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="22-1 (ХС 22-04)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="32-1 (ХС 22-01)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="32-2 (ХС 22-02)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="32-3 (ХС 22-03)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="52-1 (ХБ 22-01)", payload={"cmd": groups_keyboard_cmd})
).row().add_button(back_button).row().add_button(main_menu_button)

second_course_groups_keyboard = TextKeyboard(
    Button(label="11-1(ХЭн 21-01)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="11-2(ХЭн 21-02)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="31-1 (ХС 21-01)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="31-2 (ХС 21-02)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="51-1 (ХБ 21-01)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="61-1 (ХС 21-04)", payload={"cmd": groups_keyboard_cmd})
).row().add_button(back_button).row().add_button(main_menu_button)

third_course_groups_keyboard = TextKeyboard(
    Button(label="10-1(ХЭн 20-01)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="30-1 (ХС 20-01)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="30-2 (ХС 20-02)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="50-1 (ХБ 20-01)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="60-1 (ХС 20-04)", payload={"cmd": groups_keyboard_cmd})
).row().add_button(back_button).row().add_button(main_menu_button)

other_courses_groups_keyboard = TextKeyboard(
    Button(label="19-1(ХЭн 19-01)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="29-1 (ХС 19-04)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="37-2 (ХС 17-02)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="38-2 (ХС 18-02)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="39-1 (ХС 19-01)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="39-2 (ХС 19-02)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="59-1 (ХБ 19-02)", payload={"cmd": groups_keyboard_cmd}),
    Button(label="69-1 (ХС 19-05)", payload={"cmd": groups_keyboard_cmd})
).row().add_button(back_button).row().add_button(main_menu_button)

courses_groups = {"1 курс": first_course_groups_keyboard,
                  "2 курс": second_course_groups_keyboard,
                  "3 курс": third_course_groups_keyboard,
                  "4, 5, 6 курс": other_courses_groups_keyboard}

week_number_keyboard = TextKeyboard(
    Button(label="1", payload={"cmd": weeks_keyboard_cmd}),
    Button(label="2", payload={"cmd": weeks_keyboard_cmd}),
).row().add_button(back_button).row().add_button(main_menu_button)

weekday = TextKeyboard(
    Button(label="Понедельник", payload={"cmd": days_keyboard_cmd}),
    Button(label="Вторник", payload={"cmd": days_keyboard_cmd}),
    Button(label="Среда", payload={"cmd": days_keyboard_cmd}),
    Button(label="Четверг", payload={"cmd": days_keyboard_cmd}),
    Button(label="Пятница", payload={"cmd": days_keyboard_cmd}),
    Button(label="Суббота", payload={"cmd": days_keyboard_cmd}),
    Button(label="Все", payload={"cmd": days_keyboard_cmd})
).row().add_button(back_button).row().add_button(main_menu_button)


