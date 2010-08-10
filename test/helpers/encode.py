import json
import urllib

data = {
    'name': 'Martin Marrese',
    'age': 29,
    'address': {
        'street': 'estivao',
        'number': 133,
        'floor': 4,
        'apt': 'B'
        }
    }

print json.dumps(data)

data = {
    'name': 'Warmi Guercio',
    'age': 31,
    'address': {
        'street': 'estivao',
        'number': 133,
        'floor': 4,
        'apt': 'B'
        }
    }

print json.dumps(data)

