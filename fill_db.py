from pymongo import MongoClient
import uuid
import hashlib

client = MongoClient()
db = client.test
db.test_fetch.ensure_index("location", "2dsphere")

#Obtenido de: http://pythoncentral.io/hashing-strings-with-python/
def hash_password(password):
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def return_geopoint(longitude, latitude):
    geopoint = {
        "type" : "Point",
        "coordinates" : [ longitude, latitude ]
    }
    return geopoint

def has_password(password):
    has = 0
    if password not "":
        has= 1
    return has

def build_object_dictionary(name, description, link, crude_password, longitude, latitude):
    has_pwd = has_password(password)
    object_dictionary = {
    "name": name,
    "description": description,
    "link":link,
    "has_password" : has_pwd,
    "password": hash_password(crude_password),
    "location": return_geopoint(longitude,latitude)
    }
    return object_dictionary

#Archivos para probar cerca de "-100.2952296","25.648925"
def create_dummy_objects():
    db.test_fetch.insert_one(build_object_dictionary("Pokemon Red", "best game evuuuur", "http://pokemon-stats.com/descargas/pokemon_rojo.zip", "rojo", "-100.2952296","25.648925"))
    db.test_fetch.insert_one(build_object_dictionary("Pokemon Azul", "best game evuuuur x 2", "http://pokemon-stats.com/descargas/pokemon_azul.zip", "azul","-100.2937973","25.6483229"))
    db.test_fetch.insert_one(build_object_dictionary("Pokemon Amarillo", "best game evuuuur x 3", "http://pokemon-stats.com/descargas/pokemon_amarillo.zip", "amarillo","-100.2929175","25.6494883"))
    db.test_fetch.insert_one(build_object_dictionary("Pokemon Dorado", "best game evuuuur x 4", "http://pokemon-stats.com/descargas/pokemon_dorado.zip", "Dorado","-100.2921451","25.6506393"))
    db.test_fetch.insert_one(build_object_dictionary("Pokemon Plata", "best game evuuuur x 5", "http://pokemon-stats.com/descargas/pokemon_plata.zip", "Plata","-100.2887118","25.6315655"))
    return "Success"

create_dummy_objects()
