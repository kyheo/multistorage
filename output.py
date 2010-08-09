import json
import multistorage

def render(obj):
    if multistorage.DEBUG == True:
        return json.dumps(obj, indent=4)
    else:
        return json.dumps(obj)
