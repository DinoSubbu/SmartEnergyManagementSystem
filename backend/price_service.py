from flask import Flask
from flask import request
from prices.prices_db import PriceDB
from datetime import datetime, timedelta



app = Flask(__name__)

DBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}

priceDB = PriceDB(DBConfig)
try:
    priceDB.writePriceToDB(datetime.now())
    priceDB.writePriceToDB(datetime.now() + timedelta(days =1))
except Exception:
    pass

@app.route('/')
def index():
    return 'Price Service'

@app.route('/updateprices', methods=['POST'])
def updateprices():
    if request.method == 'POST':
        priceDB.writePriceToDB(datetime.now())
        priceDB.writePriceToDB(datetime.now() + timedelta(days =1))
        return "success", 200
    return "HTTP-Method not supported", 404

if __name__ == '__main__':
    app.run(debug=True, port=5003) #run app in debug mode on port 5003