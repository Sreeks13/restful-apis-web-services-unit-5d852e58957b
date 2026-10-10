from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.get("/basic/sensors")
def basic_sensors():
    auth = request.authorization
    if not auth or auth.username != "sensor_admin" or auth.password != "homehub_pass":
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify({"authenticated": True, "sensors": ["temperature", "humidity"]}), 200

@app.get("/bearer/sensors")
def bearer_sensors():
    if request.headers.get("Authorization") != "Bearer smart-home-demo-token":
        return jsonify({"error": "invalid token"}), 401
    return jsonify({"authenticated": True, "sensors": ["temperature", "humidity"]}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
