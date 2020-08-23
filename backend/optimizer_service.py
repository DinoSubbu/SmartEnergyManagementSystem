from flask import Flask
from flask import request
from flask_cors import CORS
from database.databasehandler import MariaDB_handler
from demandResponseOptimization.optimizer_db import Optimzer_DB
import json
from util.json_encoder import Encoder
import config

#FLASK_APP=simulation/building_service.py flask run

app = Flask(__name__)
CORS(app)

configDB = {'user':'myusr', 'password':'myusrpass', 'host':'localhost', 'port':'3306', 'database':'mydb'}
opt_db = Optimzer_DB(configDB, configDB, configDB, time_limit=config.OPTIMIZER_TIMEOUT, gap_factor=config.OPTIMIZER_GAP_FACTOR)


@app.route('/optimizer/generateSchedule', methods=['POST'])
def generateSchedule():
    if request.method == 'POST':
        opt_db.setSameObjectiveAsLastDay()
        schedules = []
        for obj_function in ['cost', 'min_buy', 'independent']:
            schedules.append(opt_db.writeScheduleToDB(obj_function))
        return json.dumps([schedule.toDict() for schedule in schedules], cls=Encoder), 200
    return "HTTP-Method not supported", 404


@app.route('/optimizer/setObjective/<string:objective>', methods=['POST'])
def setObjective(objective):
    if request.method == 'POST':
        if objective not in ['cost', 'min_buy', 'independent']:
            return "Unkown objective", 422
        return opt_db.setObjectiveInDB(objective).toJson(), 200
    return "HTTP-Method not supported", 404


if __name__ == '__main__':
    app.run(debug=True, port=5004) #run app in debug mode on port 5000