import asyncio

from secret import TOKEN
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import aiohttp
from bs4 import BeautifulSoup

from data_base import DateBase
from utils import get_message_from_links, get_keyboard, get_movie_info, async_fetch

my_base = DateBase()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message) -> None:
    await message.reply(
        "Hi, I'm a movie/series search bot. to find a movie/series,"
        " just write its name, to view the rest of the functions, click /help\n", reply_markup=get_keyboard())


@dp.message_handler(commands=['help'])
async def get_help(message: types.Message) -> None:
    await message.reply(
        "1) to find a movie/series, write its name\n"
        "2) to view the search history, write /history\n"
        "3) to view your movie/series search statistics, write /stats\n", reply_markup=get_keyboard())


@dp.message_handler(commands=['history'])
async def get_history(message: types.Message) -> None:
    history = await my_base.get_search_history(message.from_user.id)
    ans = ''
    for i in history:
        ans += i[1]
        ans += ', '
    tasks = list()
    tasks.append(message.reply(f"your history search:\n{ans}", reply_markup=get_keyboard()))
    tasks.append(my_base.close())
    await asyncio.gather(*tasks)


@dp.message_handler(commands=['stats'])
async def get_stats(message: types.Message) -> None:
    stats = await my_base.get_stats(message.from_user.id)
    ans = ''
    for i in stats:
        ans += f'{i[0]}: {i[1]}\n'
    tasks = list()
    tasks.append(message.reply(f"your stats:\n{ans}", reply_markup=get_keyboard()))
    tasks.append(my_base.close())
    await asyncio.gather(*tasks)


@dp.message_handler()
async def get_movie(message: types.Message) -> None:
    async with aiohttp.ClientSession() as session:
        response1 = async_fetch(session, f"https://www.google.com/search?q={message.text}%20смотреть%20онлайн")
        response2 = async_fetch(session, f'https://www.kinopoisk.ru/index.php?kp_query={message.text}')
        html1, html2 = await asyncio.gather(response1, response2)

    links: list[str] = []
    for paragraph in BeautifulSoup(html1, 'html.parser').find_all('a', href=True):
        if len(links) == 5:
            break
        if (paragraph.get('data-jsarwt') == "1") and (paragraph.get('data-ved')[-3:] == 'QAQ'):
            links.append(paragraph.get('href'))

    tasks = list()
    tasks.append(my_base.add_film(message.from_user.id, message.text))
    movie_info = get_movie_info(html2)
    if movie_info is None:
        tasks.append(message.reply('информация о фильме не найдена\n' + get_message_from_links(links),
                                   reply_markup=get_keyboard()))
    else:
        tasks.append(bot.send_photo(message.from_user.id, movie_info['poster'],
                                    f'{movie_info["name"]}\n{movie_info["genre"]}\nрейтинг: {movie_info["rate"]}'))
        tasks.append(message.reply(get_message_from_links(links), reply_markup=get_keyboard()))
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    executor.start_polling(dp)
