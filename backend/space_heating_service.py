from flask import Flask
from flask import request
from flask import jsonify
import config
from gasBoiler.space_heating_db import SpaceHeatingDB
from datetime import datetime, timedelta


app = Flask(__name__)

DBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}

spaceHeatingDB = SpaceHeatingDB(DBConfig, DBConfig)

@app.route('/')
def index():
    return 'Space Heating Service'


@app.route('/updateSpaceHeatingPower', methods=['POST'])
def updateSpaceHeatingPower():
    if request.method == 'POST':
        timestamp = datetime.now()
        timestamp = timestamp.replace(minute=0, second=0, microsecond=0)
        spaceHeatingDB.writePowerSHToDB(timestamp)
        return "success",200
    return "HTTP-Method not supported", 404

@app.route('/getSpaceHeatingPower', methods=['GET'])
def getSpaceHeatingPower():
    if request.method == 'GET':
        timestamp = request.args.get('timestamp')
        buildingName = request.args.get('buildingName')
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
        powerSH = spaceHeatingDB.getPowerSH(timestamp, buildingName, latitude, longitude)
        return jsonify(powerSH=powerSH, response_code=200)
    return "HTTP-Method not supported", 404

if __name__ == '__main__':
    app.run(debug=True, port=5006) #run app in debug mode on port 5006