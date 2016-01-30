from flask import Flask, Response, request
# jsonify
import simplejson as json
from pymongo import MongoClient
# import pandas as pd
# import csv
from bson import json_util
from bson.son import SON

app = Flask(__name__)

client = MongoClient()
db = client.test


def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response
app.after_request(add_cors_headers)


def query_location_files(longitude, latitude, distance=500):
    latitude = float(latitude)
    longitude = float(longitude)
    max_distance = distance
    # meters
    query = {'location': {
        '$near': SON([('$geometry', SON([
            ('type', 'Point'),
            ('coordinates', [longitude, latitude])])),
            ('$maxDistance', max_distance)])}}
    fields = {
#        "name": True,
#        "description": True,
        "link": False,
#        "has_password" : True,
        "password": False
#        "location": True
    }
    response = []
    for doc in db.test_fetch.find(query, fields):
        response.append(doc)
    return response


@app.route('/files', methods=['GET'])
def indicator():
    longitude = request.args.get('longitude')
    latitude = request.args.get('latitude')
    response = query_location_files(longitude, latitude)
    return Response(json.dumps(response,default=json_util.default), mimetype='application/json')


if __name__ == '__main__':
    app.after_request(add_cors_headers)
    app.run(threaded=True, host='0.0.0.0', debug=True)
