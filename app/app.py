from flask import Flask, jsonify, request
from redis import Redis
from pymongo import MongoClient

app = Flask(__name__)
r = Redis(host="localhost", port=6379, db=0)
mongo = MongoClient("mongodb://localhost:27017/")
db = mongo["FlaskApp"]
collection = db["Values"]

@app.route("/")
def home():
    return jsonify(message="Hello from root")

@app.route("/get", methods=["GET"])
def get():
    data = collection.find({})
    result = []
    for doc in data:
        doc.pop("_id", None)
        result.append(doc)
    return jsonify(result)

@app.route("/set", methods=["POST"])
def set():
    data = request.get_json()
    key = data.get("key")
    val = data.get("val")
    collection.update_one({"key":key}, {"$set": {"val": val}}, upsert=True)
    return jsonify(message=f"SET {key} to {val}")

if __name__ == "__main__":
    app.run(port=5000, debug=True)