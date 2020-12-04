FROM python:3.8

WORKDIR /code

COPY . .

# install dependencies
RUN pip install pip --upgrade && pip install -r requirements.txt

# start flask app
CMD python flaskapp.py




