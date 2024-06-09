from aiogram import types
import aiohttp
from bs4 import BeautifulSoup


def get_keyboard():  # type: ignore
    keyboard = types.ReplyKeyboardMarkup()
    button_1 = types.KeyboardButton(text="/help")
    keyboard.add(button_1)
    button_2 = types.KeyboardButton(text="/history")
    keyboard.add(button_2)
    button_3 = types.KeyboardButton(text="/stats")
    keyboard.add(button_3)
    return keyboard


def get_message_from_links(links: list[str]) -> str:
    message = ''
    for link in links:
        message += link.split('/')[2].split('.')[-2] + ': ' + link + '\n\n'
    return message


def get_movie_info(html: str) -> dict[str, str] | None:
    soup = BeautifulSoup(html, 'html.parser')

    parsed_html = soup.find('div', {'class': 'element most_wanted'})
    if parsed_html:
        name = parsed_html.find('p', {'class': 'name'}).find('a').text
        genre = parsed_html.findAll('span', {'class': 'gray'})[1].text
        rate = parsed_html.find('div', {'class': 'right'}).text.split('\n')[1]
        poster = f"https://www.kinopoisk.ru/images/sm_film/{parsed_html.findAll('a')[0]['href'].split('/')[2]}.jpg"
        return {'name': name, 'rate': rate, 'poster': poster, 'genre': genre}
    else:
        return None


async def async_fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Asyncronously fetch (get-request) single url using provided session
    :param session: aiohttp session object
    :param url: target http url
    :return: fetched text
    """
    headers = {
        'user-agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36'
        )
    }
    async with session.get(url, headers=headers) as response:
        text = await response.text()
    return text
