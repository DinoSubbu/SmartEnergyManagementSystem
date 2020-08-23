import requests
import json

headers = {'content-type': 'application/json'}

# solar panel
payload = """
{
	"name": "solar_1",
	"lat": "47.745837",
	"long": "8.105398",
	"powerCoefficient": 0.6,
	"area": 25,
	"angleOfModule": 45
}
"""
r = requests.post("http://127.0.0.1:5000/solarpanel/create", data=payload, headers=headers)
print(r)

payload = """
{
	"name": "solar_2",
	"lat": "47.745837",
	"long": "8.105398",
	"powerCoefficient": 0.6,
	"area": 20,
	"angleOfModule": 45
}
"""
r = requests.post("http://127.0.0.1:5000/solarpanel/create", data=payload, headers=headers)
print(r)

# wind turbine
payload = """
{
	"name": "wind_1",
	"lat": "48.745837",
	"long": "10.105398",
	"powerCoefficient": 0.6,
	"radius": 7
}
"""
r = requests.post("http://127.0.0.1:5000/windturbine/create", data=payload, headers=headers)
print(r)

payload = """
{
	"name": "wind_2",
	"lat": "48.745837",
	"long": "10.105398",
	"powerCoefficient": 0.6,
	"radius": 6
}
"""
r = requests.post("http://127.0.0.1:5000/windturbine/create", data=payload, headers=headers)
print(r)

payload = """{
	"name": "battery_1",
	"lat": "48.745837",
	"long": "9.105398",
	"batteryEfficiency": 0.95,
	"chargeUpperBound": 20000,
	"dischargeUpperBound": 20000,
	"energyUpperBound": 100000,
	"selfDischargingRate": 10
}
"""
r = requests.post("http://127.0.0.1:5000/battery/create", data=payload, headers=headers)

payload = """{
	"name": "battery_2",
	"lat": "48.745837",
	"long": "9.105398",
	"batteryEfficiency": 0.95,
	"chargeUpperBound": 10000,
	"dischargeUpperBound": 10000,
	"energyUpperBound": 50000,
	"selfDischargingRate": 10
}
"""
r = requests.post("http://127.0.0.1:5000/battery/create", data=payload, headers=headers)

print(r)

payload = """
{
	"name": "office_1",
	"lat": "48.745837",
	"long": "9.105398",
	"mathematicalModel": {
			"thermalResistance" : 0.055,
			"heatCapacityAirIndoor" : 525
		},
	"historicalData": [
		3295.45431,
		3230.50214,
		3088.39031,
		3066.93376,
		3029.34311,
		3013.018,
		2898.94943,
		2892.45014,
		3028.16952,
		3606.25,
		4247.32906,
		6434.29533,
		5214.87252,
		5814.52432,
		5659.70644,
		5093.25284,
		5255.44979,
		5019.69489,
		4628.43443,
		4269.22425,
		4071.98214,
		3855.55357,
		3606.15708,
		3414.28935
	],
	"components": [
		{
			"name": "dish_washer_1",
			"est": 9,
			"let": 18,
			"e": 1800,
			"lot": 2
		},
		{
			"name": "dish_washer_2",
			"est": 9,
			"let": 12,
			"e": 1800,
			"lot": 2
		},
		{
			"name": "dish_washer_3",
			"est": 9,
			"let": 12,
			"e": 1800,
			"lot": 2
		},
		{
			"name": "dish_washer_4",
			"est": 9,
			"let": 12,
			"e": 1800,
			"lot": 2
		},
		{
			"name": "vacuum_cleaner_1",
			"est": 7,
			"let": 10,
			"e": 1200,
			"lot": 1
		},
		{
			"name": "vacuum_cleaner_2",
			"est": 7,
			"let": 9,
			"e": 1200,
			"lot": 1
		},
		{
			"name": "vacuum_cleaner_3",
			"est": 19,
			"let": 21,
			"e": 1200,
			"lot": 1
		},
		{
			"name": "vacuum_cleaner_4",
			"est": 19,
			"let": 23,
			"e": 1200,
			"lot": 1
		},
		{
			"name": "electrical_vehicle_1",
			"est": 8,
			"let": 18,
			"e": 3500,
			"lot": 3
		},
		{
			"name": "electrical_vehicle_2",
			"est": 18,
			"let": 24,
			"e": 3500,
			"lot": 3
		}
	]
}
"""
r = requests.post("http://127.0.0.1:5000/building/create", data=payload, headers=headers)
print(r)

payload = """
{
	"name": "home_1",
	"lat": "48.745837",
	"long": "9.105398",
	"mathematicalModel": {
			"thermalResistance" : 0.018,
			"heatCapacityAirIndoor" : 525
		},
	"historicalData": [
		332.1709,
		262.819,
		234.3779,
		229.2816,
		235.4617,
		255.1405,
		283.4671,
		432.1225,
		534.3769,
		559.6205,
		608.4645,
		585.9718,
		648.3234,
		668.8364,
		557.5756,
		526.7263,
		550.5535,
		529.8151,
		641.3157,
		754.156,
		782.5452,
		740.9206,
		597.4084,
		475.6613
	],
	"components": [
		{
			"name": "washing_machine",
			"est": 9,
			"let": 17,
			"e": 2000,
			"lot": 2
		},
		{
			"name": "dish_washer",
			"est": 9,
			"let": 12,
			"e": 1800,
			"lot": 2
		},
		{
			"name": "spin_dryer",
			"est": 13,
			"let": 18,
			"e": 2500,
			"lot": 1
		},
		{
			"name": "electrical_vehicle",
			"est": 18,
			"let": 24,
			"e": 3500,
			"lot": 3
		},
		{
			"name": "vacuum_cleaner",
			"est": 9,
			"let": 17,
			"e": 1.2,
			"lot": 1
		}
	]
}
"""
r = requests.post("http://127.0.0.1:5000/building/create", data=payload, headers=headers)
print(r)

r = requests.post("http://127.0.0.1:5001/updateWeather")
print(r)

r = requests.post("http://127.0.0.1:5003/updateprices")
print(r)

r = requests.post("http://127.0.0.1:5002/simulation/init")
print(r)

r = requests.post("http://127.0.0.1:5002/simulation/forecast")
print(r)

r = requests.post("http://127.0.0.1:5004/optimizer/generateSchedule")
print(r)

for i in range(40):
	r = requests.post("http://127.0.0.1:5002/simulation/nextHour")
	print(r)
