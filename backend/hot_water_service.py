from flask import Flask
from flask import request
from flask import jsonify
import config
from gasBoiler.hot_water_demand_db import HotWaterDB
from datetime import datetime, timedelta


app = Flask(__name__)

DBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}

hotWaterDB = HotWaterDB(DBConfig, DBConfig)

@app.route('/')
def index():
    return 'Hot Water Service'


@app.route('/updateHotWaterPower', methods=['POST'])
def updateHotWaterPower():
    if request.method == 'POST':
        timestamp = datetime.now()
        timestamp = timestamp.replace(minute=0, second=0, microsecond=0)
        hotWaterDB.writePowerDHWToDB(timestamp)
        return "success", 200
    return "HTTP-Method not supported", 404

@app.route('/getHotWaterPower', methods=['GET'])
def getHotWaterPower():
    if request.method == 'GET':
        timestamp = request.args.get('timestamp')
        buildingName = request.args.get('buildingName')
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
        powerDHW = hotWaterDB.getPowerDHW(timestamp, buildingName, latitude, longitude)
        return jsonify(powerDHW=powerDHW, response_code=200)
    return "HTTP-Method not supported", 404

if __name__ == '__main__':
    app.run(debug=True, port=5007) #run app in debug mode on port 5007
