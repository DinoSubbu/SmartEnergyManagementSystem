from flask import Flask
from flask import request
from flask_cors import CORS
from database.databasehandler import MariaDB_handler
from simulation.simulation import Simulation
from datetime import datetime

#FLASK_APP=simulation/building_service.py flask run

app = Flask(__name__)
CORS(app)

configDB = {'user':'myusr', 'password':'myusrpass', 'host':'localhost', 'port':'3306', 'database':'mydb'}
sim = None

@app.route('/simulation/init', methods=['POST'])
def init_simulation():
    if request.method == 'POST':
        global sim
        if sim == None:
            sim = Simulation(configDB, configDB, configDB)
            sim.init_sim(datetime.now())
            return "success", 201
        else:
            return "conflict", 409
    return "HTTP-Method not supported", 404

@app.route('/simulation/undo', methods=['POST'])
def undo_simulation():
    if request.method == 'POST':
        global sim
        if sim != None:
            sim.close_sim()
            sim = None
            return "success", 200
        else:
            return "conflict", 409
    return "HTTP-Method not supported", 404

@app.route('/simulation/nextHour', methods=['POST'])
def nextHour():
    if request.method == 'POST':
        if sim != None:
            sim.simulateNextHour()
            return "success", 200
        else:
            return "no simulation is initialized", 404
    return "HTTP-Method not supported", 404

@app.route('/simulation/nextHour/<string:time_str>', methods=['POST'])
def nextHourWithDate(time_str):
    if request.method == 'POST':
        if sim != None:
            time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
            time = time.replace(minute=0, second=0)
            if time > sim.time:
                time_diff = time - sim.time
                hours = int(round(time_diff.total_seconds())/(60*60))
                for i in range(hours+1):
                    sim.simulateNextHour()
            return "success", 200
        else:
            return "no simulation is initialized", 404
    return "HTTP-Method not supported", 404


@app.route('/simulation/forecast', methods=['POST'])
def forecast():
    if request.method == 'POST':
        if sim != None:
            sim.simulateForecast()
            return "success", 200
        else:
            return "no simulation is initialized", 404
    return "HTTP-Method not supported", 404

if __name__ == '__main__':
    app.run(debug=True, port=5002) #run app in debug mode on port 5000