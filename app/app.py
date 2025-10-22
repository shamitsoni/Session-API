from flask import Flask, jsonify, request
from redis import Redis

app = Flask(__name__)
r = Redis(host="localhost", port=6379, db=0)

@app.route("/")
def home():
    return jsonify(message="Hello from root")

@app.route("/get", methods=["GET"])
def get():
    keys = r.keys("*")
    result = {}
    for key in keys:
        key_str = key.decode("utf-8")
        val = r.get(key)
        if val is not None:
            val_str = val.decode("utf-8")
        else:
            val_str = None
        result[key_str] = val_str
    return jsonify(result)

@app.route("/set", methods=["POST"])
def set():
    data = request.get_json()
    key = data.get("key")
    val = data.get("val")
    r.set(key, val)
    return jsonify(message=f"SET {key} to {val}")

if __name__ == "__main__":
    app.run(port=5000, debug=True)