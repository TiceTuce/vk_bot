import pandas as pd
import aiohttp
import asyncio
import bs4
import re
import aiofiles
from Lesson import Lesson
from pathlib import Path
from config import path_to_excel_ttb


async def update_excel_file():
    url_excel_file = await get_excel_download_link_from_site("https://khti.ru/obuchenie/raspisanie-zanyatiy.php")
    await download_excel_file(url_excel_file, 'timetables/timetable.xls')


async def get_excel_download_link_from_site(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            domain = 'https://' + response.host
            html = await response.text()
            soup = bs4.BeautifulSoup(html, 'lxml')

            sample = re.compile('Расписание (весеннего|зимнего|осеннего) семестра')
            result = soup.find('div', 'inner-page-content').find(string=sample).find_next('a')
            excel_file_link = domain + result.get('href')

            return excel_file_link


async def download_excel_file(url: str, path: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                async with aiofiles.open(path, mode='wb+') as excel_file:
                    excel = await response.content.read()
                    await excel_file.write(excel)
            except PermissionError as pe:
                print(pe)


def get_data_from_excel(excel: Path):
    file = pd.ExcelFile(excel)

    timetable = []
    for course in file.sheet_names:
        course_timetable = get_data_from_sheet(file, course)
        timetable.extend(course_timetable)

    return timetable


def get_data_from_sheet(excel, sheet_name) -> tuple[Lesson]:
    sheet = pd.read_excel(excel, sheet_name=sheet_name, skiprows=4, skipfooter=2)

    # Format table
    _format_table(sheet)

    rows_info = []
    for index, content in sheet.iterrows():
        for group in range(3, len(content.keys())):
            row = Lesson(
                course=sheet_name,
                group=content.keys()[group],
                week_number=content['Неделя'],
                week_day=content['День'],
                pair_time=content['Пара'],
                lesson_info=content[group],
            )

            rows_info.append(row)

    return tuple(rows_info)


def _format_table(table: pd.DataFrame) -> None:
    table.drop(index=[i for i in range(42, 50)], inplace=True)  # delete 48-54 lines (see excel file)
    table['Неделя'].fillna(method='ffill', inplace=True)
    table['День'].fillna(method='ffill', inplace=True)
    table.fillna(value='―'*6, inplace=True)
    table['Неделя'].replace(['1-я неделя', '2-я неделя'], [1, 2], inplace=True)


async def main():
    await update_excel_file()
    get_data_from_excel(path_to_excel_ttb)
    # download_link = await get_excel_download_link_from_site("https://khti.ru/obuchenie/raspisanie-zanyatiy.php")
    # path = 'timetables/timetable.xls'
    # await download_excel_file(download_link, 'timetables/timetable.xls')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
