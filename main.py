import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
#app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description=db.Column(db.String(100),nullable=False)
    humidity=db.Column(db.Integer)
    temp_min=db.Column(db.Integer)
    temp_max=db.Column(db.Integer)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'
    r = requests.get(url).json()
    return r

@app.route('/')
def index_get():
    cities = City.query.all()
    print(cities)

    weather_data = []

    for city in cities:

        r = get_weather_data(city.name)
        #print(r)

        weather = {
            "id":city.id,
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
            'humidity':r['main']['humidity'],
            'temp_min':r['main']['temp_min'],
            'temp_max':r['main']['temp_max']
        }

        weather_data.append(weather)
        # print(weather_data)


    return render_template('weather.html', weather_data=weather_data)

@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')
        
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)
            print(new_city_data)
            desc = new_city_data['weather'][0]['description']
            hum=new_city_data['main']['humidity']
            min_temp=new_city_data['main']['temp_min']
            max_temp=new_city_data['main']['temp_max']
            
            
            

            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city,
                description=desc,humidity=hum,temp_min=min_temp,temp_max=max_temp)

                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'City does not exist in the world!'
        else:
            err_msg = 'City already exists!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added succesfully!')

    return redirect(url_for('index_get'))

@app.route('/delete/<int:id>')
def delete_city(id):
    city = City.query.filter_by(id=id).first()
    db.session.delete(city)
    db.session.commit()

    # flash(f'Successfully deleted { city.name }', 'success')
    return redirect(url_for('index_get'))

if __name__ == '__main__':
    app.run(debug=True)