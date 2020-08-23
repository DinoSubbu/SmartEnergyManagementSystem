# Development of CO2 and Gas Boiler Service for EMS

## Install
How to install the requirements for starting the database, the backend and the frontend. In the following we assume that docker, docker-compose, nodejs, python3, pip3 and angular are installed.

### Start Database and Backend
* Startup docker service (possibly with `sudo systemctl start docker`)
* change directory to backend
* `docker-compose build` (possibly with `sudo`)
* `pip3 install -r requirements.txt`
* `docker-compose up` (possibly with `sudo`)
* Check if database is running on http://localhost:8080
* `python3 optimizer_service.py`

### Start Frontend
* Change directory to frontend
* Execute the command `npm install` to install packages necessary for the project automatically.
* `ng serve --open`




