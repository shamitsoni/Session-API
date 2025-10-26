import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from redis import Redis
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
r = Redis(host="localhost", port=6379, db=0)
mongo = MongoClient("mongodb://localhost:27017/")
db = mongo["FlaskApp"]
collection = db["Values"]

CACHE_TTL = 30

@app.route("/")
def home():
    return jsonify(message="Hello from root")

# Retrieve a specific pair
@app.route("/get/<key>", methods=["GET"])
def get_key(key):
    # Check Redis cache first
    val = r.get(key)
    if val is not None:
        r.expire(key, CACHE_TTL)
        return jsonify({key: val.decode("utf-8"), "source": "redis"})
    
    # Not in the cache --> retrieve from MongoDB
    document = collection.find_one({"key": key})
    if document:
        val = document["val"]
        r.setex(key, CACHE_TTL, val)
        return jsonify({key: val, "source": "mongodb"})
    
    return jsonify(error="Key not found"), 404

# Retrieve all pairs
@app.route("/get", methods=["GET"])
def get():
    data = collection.find({})
    result = []
    for doc in data:
        doc.pop("_id", None)
        result.append(doc)
    return jsonify(result)

# Set a pair
@app.route("/set", methods=["POST"])
def set():
    data = request.get_json()
    key = data.get("key")
    val = data.get("val")

    # Store in MongoDB
    collection.update_one({"key":key}, {"$set": {"val": val}}, upsert=True)

    # Store in Redis
    r.setex(key, CACHE_TTL, val)
    return jsonify(message=f"SET {key} to {val}")

# Delete a pair
@app.route("/delete/<key>", methods=["DELETE"])
def delete_key(key):
    in_cache = r.exists(key)
    in_database = collection.find_one({"key": key}) is not None
    if not in_cache and not in_database:
        return jsonify(message=f"ERROR: Key {key} does not exist!")
    
    r.delete(key)
    collection.delete_one({"key": key})
    return jsonify(message=f"DELETED {key}")