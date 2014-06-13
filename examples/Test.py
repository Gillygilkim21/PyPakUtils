from API import *
import time
import random
import request
api = SensorAPI()
timestamp = int(round(time.time() - 100000000) * 1000)

#for i in range(100):
#    time.sleep(0.01)
#    print api.singlePut(api.now(), 10 +random.randint(10, 20))
#time.sleep(10)


#value = got data from sensor

config = Configuration.Configuration()
config.sensorID = 12341234
config.saveConfiguration()

#print api.singleQuery(start = timestamp, location = "unknown", sensorID = "37109", sensorType = "37109")
print api.singlePut(api.now(), value, config)
