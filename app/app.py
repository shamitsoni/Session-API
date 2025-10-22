from flask import Flask, jsonify, request

app = Flask(__name__)

dict = {}

@app.route("/")
def home():
    return jsonify(message="Hello from root")

@app.route("/get", methods=["GET"])
def get():
    return jsonify(dict)

@app.route("/set", methods=["POST"])
def set():
    data = request.get_json()
    key = data.get("key")
    val = data.get("val")
    dict[key] = val
    return jsonify(message=f"COMPLETE: {key} set to {val}")

if __name__ == "__main__":
    app.run(port=5000, debug=True)