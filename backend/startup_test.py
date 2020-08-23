import simulation_service
import frontend_service
import weather_service
import price_service
import optimizer_service
import threading 

t1 = threading.Thread(target=simulation_service.app.run, kwargs=dict(debug=False, port=5002))
t2 = threading.Thread(target=price_service.app.run, kwargs=dict(debug=False, port=5003))
t3 = threading.Thread(target=weather_service.app.run, kwargs=dict(debug=False, port=5001))
t4 = threading.Thread(target=frontend_service.app.run, kwargs=dict(debug=False, port=5000))
t5 = threading.Thread(target=optimizer_service.app.run, kwargs=dict(debug=False, port=5004))

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()

