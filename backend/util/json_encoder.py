import json
import datetime

'''Create an encoder subclassing JSON.encoder. 
Make this encoder aware of our classes (e.g. datetime.datetime objects) 
'''
class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)