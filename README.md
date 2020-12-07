# mosmetro_news

Тестовое задание от Московский метрополитен

Задание: Написать API, которое получает новости за заданный период из базы, которую пополняет воркер, который каждые 10 минут парсит новости.
Новости с сайта: https://mosmetro.ru/press/news/.

По endpoint'у /news?days= возвращаются новости за указанный период дней.

Использован стек: flask, celery, postresql.

Запуск


Склонируйте репозиторий и выполните:

- Создайте файл .env с переменными окружения, к примеру:

  BROKER_URL=redis://redis_broker_container:6379/0
  
  DATABASE_URL=postgresql://postgres:123123@db/postgres
  
  DB_NAME=postgres
  
  DB_USER=postgres
  
  DB_PASSWORD=123123
  


  POSTGRES_USER=postgres
  
  POSTGRES_PASSWORD=123123
  
  POSTGRES_DB=postgres
  
  
- docker-compose build
- docker-compose up

Каждые 10 минут celery worker будет парсить сайт с новостями и заполнять новыми новостями базу.
Для получения новостей за последние n дней нужно обратиться по адресу http://127.0.0.1:500/news?days=n 
