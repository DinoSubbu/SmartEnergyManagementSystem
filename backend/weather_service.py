from flask import Flask
from flask import request
from flask import jsonify
from flask import json
from weather.weather_db import WeatherDB
from weather.weather_api import WeatherAPI


app = Flask(__name__)

DBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}

weatherDB = WeatherDB(DBConfig, DBConfig)
weatherAPI = WeatherAPI()

@app.route('/')
def index():
    return 'Weather Service'

@app.route('/updateWeather', methods=['POST'])
def updateWeather():
    if request.method == 'POST':
        weatherDB.writeWeatherToDB()
        return "success", 200
    return "HTTP-Method not supported", 404

@app.route('/currentWeather', methods=['GET'])
def getCurrentWeather():
    if request.method == 'GET':
        lat = request.args.get('lat')
        longi = request.args.get('longi')
        currentWeatherData = weatherAPI.getCurrent(lat,longi)
        return jsonify(currentWeatherData=currentWeatherData, response_code=200)
    return "HTTP-Method not supported", 404


if __name__ == '__main__':
    app.run(debug=True, port=5001) #run app in debug mode on port 5001
