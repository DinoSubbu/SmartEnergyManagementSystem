from flask import Flask
from flask import request
from co2.co2_db import Co2DB
from datetime import datetime, timedelta


app = Flask(__name__)

DBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}

co2DB = Co2DB(DBConfig)
try:
    co2DB.writeCo2ValuesToDB()
except Exception:
    pass

@app.route('/')
def index():
    return 'Co2 Service'

@app.route('/updateco2values', methods=['POST'])
def updateCo2Values():
    if request.method == 'POST':
        co2DB.writeCo2ValuesToDB()
        return "success", 200
    return "HTTP-Method not supported", 404

if __name__ == '__main__':
    app.run(debug=True, port=5005) #run app in debug mode on port 5005
