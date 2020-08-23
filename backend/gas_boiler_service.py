from flask import Flask
from flask import request, json
import requests
import config
from gasBoiler.gas_boiler_db import GasBoilerDB
from datetime import datetime, timedelta
import time


app = Flask(__name__)

DBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}

gasBoilerDB = GasBoilerDB(DBConfig,DBConfig)

@app.route('/')
def index():
    return 'Gas Boiler Service'

@app.route('/gasBoilerService', methods=['POST'])
def updateBoilerInput():
    if request.method == 'POST':
        timestamp = datetime.now()
        timestamp = timestamp.replace(minute=0, second=0, microsecond=0)
        gasBoilerDB.writeFuelInputToDB(timestamp)
        return "success", 200
    return "HTTP-Method not supported", 404

if __name__ == '__main__':
    app.run(debug=True, port=5008) #run app in debug mode on port 5008
