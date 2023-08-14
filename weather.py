# import requests
# def get_weather_data(city):
#     url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'
#     r = requests.get(url).json()
#     print(r)

# city = input("Enter City:")
# get_weather_data(city)

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///weather.db"

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)

def get_weather_report(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'
    r = requests.get(url).json()
    return r

@app.route('/')
def index():

    city_data = City.query.all()
    #print(city_data)
    weather_data=[]
    for city in city_data:
        r = get_weather_report(city.name)
        #print(r)
        weather = {
            "city":city.name,
            "temperature":r['main']['temp'],
            "description":r['weather'][0]['description'],
            "icon":r['weather'][0]['icon'],
            "main":r['weather'][0]['main']
        }
        weather_data.append(weather)
    print(weather_data)
    #return "city_data"
    return render_template('weather.html',weather_data=weather_data)

@app.route('/')
def index_post():
    cityName = request.form.get('cityName')
    error_msg = ''

    if cityName:
        existing_city = City.query.filter_by(name=cityName).first()
        if not existing_city:
            new_city_data = get_weather_data(cityName)
            if new_city_data['cod'] == 200:
                new_city = City(name=cityName)
                db.session.add(new_city)
                db.session.commit()
            else:
                error_msg = "City not existed"
        else:
            error_msg = "City Already exists"


if __name__ == '__main__':
    app.run(debug=True)