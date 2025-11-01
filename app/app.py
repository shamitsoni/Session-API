import os
import uuid
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from redis import Redis
from pymongo import MongoClient
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
r = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0)
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["FlaskApp"]
collection = db["Values"]

CACHE_TTL = 30
DB_TTL = 60

@app.route("/")
def home():
    return jsonify(message="Hello from root")

# Create a session
@app.route("/session", methods=["POST"])
def create_session():
    data = request.get_json()
    user_id = data.get("user_id")
    session_data = data.get("session_data")
    
    if not user_id or not session_data:
        return jsonify(message="Invalid body: please include user_id and session_data"), 400

    session_id = str(uuid.uuid4())

    # Store in MongoDB
    expires_at = datetime.now() + timedelta(seconds=DB_TTL)
    collection.update_one(
        {"session_id": session_id},
        {"$set": {
            "user_id": user_id, 
            "session_data": session_data,
            "expires_at": expires_at
        }},
        upsert=True
    )

    # Store in Redis
    r.setex(session_id, CACHE_TTL, str(session_data))
    return jsonify(message="Session created", session_id=session_id)

# Retrieve a session
@app.route("/session/<session_id>", methods=["GET"])
def get_session(session_id):
    # Check Redis cache first
    session_data = r.get(session_id)
    if session_data is not None:
        # Reset the expiration time in Redis and MongoDB
        r.expire(session_id, CACHE_TTL)
        expires_at = datetime.now() + timedelta(seconds=DB_TTL)
        collection.update_one(
            {"session_id": session_id}, 
            {"$set": {"expires_at": expires_at}}
        )
        return jsonify(session_id=session_id, session_data=session_data.decode("utf-8"), source="redis")
    
    # Not in the cache --> retrieve from MongoDB
    document = collection.find_one({"session_id": session_id})
    if document:
        session_data = document["session_data"]
        # Add to Redis cache and reset expiration time in MongoDB
        r.setex(session_id, CACHE_TTL, str(session_data))
        expires_at = datetime.now() + timedelta(seconds=DB_TTL)
        collection.update_one(
            {"session_id": session_id}, 
            {"$set": {"expires_at": expires_at}}
        )
        return jsonify(session_id=session_id, session_data=session_data, source="mongodb")

    return jsonify(error="Session not found"), 404

# Delete a session
@app.route("/session/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    in_cache = r.exists(session_id)
    in_database = collection.find_one({"session_id": session_id}) is not None
    if not in_cache and not in_database:
        return jsonify(error="Session not found"), 404
    
    r.delete(session_id)
    collection.delete_one({"session_id": session_id})
    return jsonify(message=f"Session {session_id} deleted")