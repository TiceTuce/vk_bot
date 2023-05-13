from typing import NamedTuple


class Lesson(NamedTuple):
    course: str
    group: str
    week_number: int
    week_day: str
    pair_time: str
    lesson_info: str

