import requests
from flask import Flask, render_template, request, redirect, flash
import sys
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from os import urandom

app = Flask(__name__, template_folder='templates', static_folder='static')

SECRET_KEY = urandom(24)
APP_ID = '64f890b614efedb225a259e52c23c24d'

app.config.update(
    {'SQLALCHEMY_TRACK_MODIFICATIONS': False,
     'SQLALCHEMY_DATABASE_URI': 'sqlite:///database.db',
     'SECRET_KEY': SECRET_KEY,
     }
)

db = SQLAlchemy(app)


def get_local_time(timezone):
    return datetime.utcnow() + timedelta(seconds=int(timezone))


def get_part_of_the_day(time_stamp):
    hour = time_stamp.hour
    parts_of_the_day = ((5, 12, 'morning'), (12, 17, 'afternoon'),
                        (17, 21, 'evening'), (21, 24, 'night'), (0, 5, 'night')
                        )
    for day_part in parts_of_the_day:
        if day_part[0] <= hour < day_part[1]:
            return day_part[2]


def get_city_id(city_name, APP_ID):
    city_id, city = None, None
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': city_name, 'type': 'like', 'units': 'metric', 'APPID': APP_ID})
        data = res.json()
        city = data['list'][0]['name']
        city_id = data['list'][0]['id']
    except Exception as e:
        print(e)
    return city_id, city


def get_city_info(city_id, APP_ID):
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city_id, 'units': 'metric', 'lang': 'en', 'APPID': APP_ID})
    data = res.json()
    current_temperature = round(data['main']['temp'])
    current_weather = data['weather'][0]['description']
    timezone = data['timezone']
    return current_temperature, current_weather, timezone


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name


@app.route('/', methods=['POST', 'GET'])
def index():
    weather_list = []

    if request.method == 'GET':
        all_rows = City.query.all()
        for row in all_rows:
            city_id, city = get_city_id(row.name, APP_ID)
            current_temperature, current_weather, timezone = get_city_info(city_id, APP_ID)

            weather_list.append(
                {'time': get_part_of_the_day(get_local_time(timezone)),
                 'name': city,
                 'current_temperature': current_temperature,
                 'current_weather': current_weather}
            )
        return render_template('index.html', weather=weather_list)

    elif request.method == 'POST':
        city_name = request.form["city_name"]
        city_id, city = get_city_id(city_name, APP_ID)
        if city_id is None:
            flash("The city doesn't exist!")
        elif db.session.query(City.id).filter_by(name=city).scalar() is not None:
            flash("The city has already been added to the list!")
        else:
            city = City(name=city)
            db.session.add(city)
            db.session.commit()

        return redirect('/')


@app.route('/del/<city_name>', methods=['POST', 'GET'])
def delete(city_name):
    city = City.query.filter_by(name=city_name).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    db.create_all()
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
