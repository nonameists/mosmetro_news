import os

from celery import Celery
from celery.schedules import crontab
from flask import Flask, request
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

from parser import MetroNews

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['CELERY_BROKER_URL'] = os.environ.get('BROKER_URL')

# для парсинга новостей "раз в 10 минут" будеи использовать Celery
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])

# настройки celery с какой переодичностью запускать задачу
celery.conf.beat_schedule = {
    # Выполнять каждые 10 минут
    'periodic_task-every-minute': {
        'task': 'check_news_taks',
        'schedule': crontab(minute='*/10')
    }
}


ma = Marshmallow(app)
db = SQLAlchemy(app)
api = Api(app)


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=True)
    date = db.Column(db.Date, nullable=False)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title


# serializer для записей из базы
class NewsSchema(ma.Schema):
    class Meta:
        fields = ("title", "url", "image", "date")
        model = News


# endpoint для получения новостей
class NewsAPI(Resource):
    def get(self):
        # забираются переданные дни
        days = int(request.args['days'])
        # запрос в базу и берем срез за кол-во дней указанных в запросе
        news = News.query.all()[:days]
        return news_schema.dump(news)


@celery.task(name="check_news_taks")
def check_news() -> None:
    # объявляем объект класса MetroNews
    metro_n = MetroNews()
    # забираем новости
    news_list = metro_n.get_news()
    # с помощью функции news_is_exist смотрим, если новость уже есть в базе то не записываем её
    # в обратном случае записываем в бд
    for news in news_list:
        if news_is_exists(news['title']):
            news_to_db = News(title=news['title'], url=news['url'], image=news['image'], date=news['date'])
            db.session.add(news_to_db)
            db.session.commit()
            # тут я просто распечатываю, что новость добавлена в бд. Для наглядности при запуске docker-compose
            print(f"news {news['title']} added to db")
        else:
            # тут я просто распечатываю, что новость не добавлена в бд. Для наглядности при запуске docker-compose
            print(f"news {news['title']} is exist")


def news_is_exists(title) -> bool:
    """
    На вход получаем заголовок новости.
    Если такая новость есть в базе возвращаем False. В обратном случае True
    """
    news = News.query.filter_by(title=f'{title}').count()
    if not news:
        return True
    return False


news_schema = NewsSchema(many=True)
api.add_resource(NewsAPI, '/news', endpoint='news')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)