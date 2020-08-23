import simulation_service
import frontend_service
import weather_service
import price_service
#import optimizer_service
import scheduler_service
import co2_service
import gas_boiler_service
import hot_water_service
import space_heating_service
import threading
import time
from initDatabases import initDatabases

t1 = threading.Thread(target=simulation_service.app.run, kwargs=dict(debug=False, port=5002))
t2 = threading.Thread(target=price_service.app.run, kwargs=dict(debug=False, port=5003))
t3 = threading.Thread(target=weather_service.app.run, kwargs=dict(debug=False, port=5001))
t4 = threading.Thread(target=frontend_service.app.run, kwargs=dict(debug=False, port=5000))
#t5 = threading.Thread(target=optimizer_service.app.run, kwargs=dict(debug=False, port=5004))
t6 = threading.Thread(target=co2_service.app.run, kwargs=dict(debug=False, port=5005))
t7 = threading.Thread(target=space_heating_service.app.run, kwargs=dict(debug=False, port=5006))
t8 = threading.Thread(target=hot_water_service.app.run, kwargs=dict(debug=False, port=5007))
t9 = threading.Thread(target=gas_boiler_service.app.run, kwargs=dict(debug=False, port=5008))

s = scheduler_service.Scheduler()
t10 = threading.Thread(target=s.run)

t1.start()
t2.start()
t3.start()
t4.start()
#t5.start()


# After starting dependant services, initialise the database with entities
time.sleep(30)
initDatabases()


t6.start()
t7.start()
t8.start()
t9.start()
t10.start()


