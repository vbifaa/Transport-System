FROM python:3.10

WORKDIR /code

COPY . .

RUN pip3 install -r requirements.txt

CMD gunicorn transport_system.wsgi:application --bind 0.0.0.0:8000
