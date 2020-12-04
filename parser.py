import bs4
import requests
from bs4 import BeautifulSoup as soup
from datetime import datetime, timedelta


class MetroNews:
    url = 'https://mosmetro.ru/press/news'
    base_url = 'https://mosmetro.ru'

    def get_news(self) -> list:
        """
        Метод get_news возвращает список со словарями.
        Словарь имеет ключи title, url, image, date
        """
        # получем сырые данные и обрабатываем их с помощью bs4
        raw_content = requests.get(self.url).content
        content = soup(raw_content, 'html.parser')

        # ищутся div'ы с новостями
        raw_news = content.find_all('div', class_=['newslist__list-item', 'newslist__list-item_warning'])

        # с помощью метода __parse_news сырые данные по каждой новости прверащаются в словарь
        news = [self.__parse_news(item) for item in raw_news]

        return news

    def __parse_news(self, news_item: bs4.element.Tag) -> dict:
        """
        Метод получает на выход сырые данные новости(bs4.element.Tag)
        парсит их и возвращает словарь
        """

        # получем url новости
        url = self.base_url + news_item.find('a', class_='newslist__link').get('href')

        # получем url изображения. Изображений нет у элементов с классом newslist__list-item_warning
        # обычно это новости о закрытом вестибюле/остуствие движений на станциях
        image = news_item.find('img', class_='newslist__image')
        if image:
            image = self.base_url + image.get('src')
        # заголовок новости
        title = news_item.find('span', class_='newslist__text-title').getText(strip=True)

        '''
        Тут забираем сырые данные о времени публикации прямо из div'а новости в классе newslist__text-time
        Там может писать - опубликовано 12 минут, 20 часов, 2 недели, 1 месяц назад итд
        Забирается от сюда из-за того, по некоторым новостям невозможно перейти. У них присутствует url по
        которому можно перейти, но по нему открывается не новость, а снова страница всех новостей.
        
        На некоторые новости переходит корректно и там дата публикации указывается вида: 1 декабря 2020 года.
        Но из-за того, что не все новости так корректно работают было принятно решение забирать дату данным образом
        и парсить её с помощью метода __get_published_date
        '''
        raw_published = news_item.find('span', class_='newslist__text-time').getText(strip=True)
        published_date = self.__get_published_date(raw_published)

        return {
            'title': title,
            'url': url,
            'image': image,
            'date': published_date
        }

    @staticmethod
    def __get_published_date(text_time: str) -> datetime.date:
        """
        Метод получает на вход дату в виде строки вида: '20 минут назад'.
        Смотрим в какой единице изменерия указано время (часы, день, неделя, месяц).
        И переводит значение в минуты.
        После этого для получения актуальной даты публикации новости из текущей даты вычитается
        время в минутах от даты публикации
        """
        time_dict = {
            'hour': 60,
            'day': 1440,
            'week': 10080,
            'month': 43800
        }

        # текущая дата
        current_time = datetime.today().date()

        raw_time = text_time.split()
        # количетсво единиц
        time_amount = int(raw_time[0])
        # единица измерения (миныт, часы, недели итд)
        time_unit = raw_time[1]

        # в зависимости от еденицы измерения вычисляется сколько минут назад была опубликована новость
        if time_unit.startswith('ч'):
            minutes = timedelta(minutes=time_dict['hour'] * time_amount)
        elif time_unit.startswith('д'):
            minutes = timedelta(minutes=time_dict['day'] * time_amount)
        elif time_unit.startswith('н'):
            minutes = timedelta(minutes=time_dict['week'] * time_amount)
        elif time_unit.startswith('мес'):
            minutes = timedelta(minutes=time_dict['month'] * time_amount)
        else:
            minutes = timedelta(minutes=time_amount)

        date_published = current_time - minutes

        return date_published
