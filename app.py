from flask import Flask, Response, request
# jsonify
import simplejson as json
from pymongo import MongoClient
# import pandas as pd
# import csv
from bson import json_util
from bson.son import SON
from hashlib import sha1
import time, os, base64, urllib, hmac

app = Flask(__name__)

client = MongoClient()
db = client.test

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
S3_BUCKET = os.environ.get('S3_BUCKET')

def has_password(password):
    has = 0
    if password is not "":
        has= 1
    return has

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
def files():
    longitude = request.args.get('longitude')
    latitude = request.args.get('latitude')
    response = query_location_files(longitude, latitude)
    return Response(json.dumps(response,default=json_util.default), mimetype='application/json')


@app.route('/file/upload/request', methods=['POST'])
def upload():
    object_name = urllib.quote_plus(request.args.get('file_name'))
    mime_type = request.args.get('file_type')

    expires = int(time.time()+60*60*24)
    amz_headers = "x-amz-acl:public-read"

    string_to_sign = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)

    signature = base64.encodestring(hmac.new(AWS_SECRET_KEY.encode(), string_to_sign.encode('utf8'), sha1).digest())
    signature = urllib.quote_plus(signature.strip())

    url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, object_name)

    content = json.dumps({
        'signed_request': '%s?AWSAccessKeyId=%s&Expires=%s&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
        'url': url,
    })
    return Response(json.dumps(response,default=json_util.default), mimetype='application/json')

@app.route("/file/upload/register", methods=["POST"])
def submit_form():
    document = {
    "name" : request.form["name"],
    "description" : request.form["description"],
    "link" : request.form["link"],
    "has_password" = request.form["has_password"],
    "password" = request.form["password"],
    "location" = request.form[return_geopoint(request.form["longitude"],request.form["latitude"])]
    }
    db.test_fetch.insert_one(document)
    response = [{"status":"200"}]
    return Response(json.dumps(response,default=json_util.default), mimetype='application/json')


@app.route('/file/download', methods=['POST'])
def download( ):
    return Response(json.dumps(response,default=json_util.default), mimetype='application/json')

if __name__ == '__main__':
    app.after_request(add_cors_headers)
    app.run(threaded=True, host='0.0.0.0', debug=True)
