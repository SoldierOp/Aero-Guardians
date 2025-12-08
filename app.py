import pandas as pd
import os
from flask import Flask, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)

# Ensure data directory exists
os.makedirs("data", exist_ok=True)


@app.route("/")
def index():
    return "Server is running"


def fetch_live_data():
    """Fetch live air quality data for Mumbai from Open-Meteo API."""
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": 19.0760,          # Mumbai coordinates
        "longitude": 72.8777,
        "hourly": "pm2_5,pm10",
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Take the latest available hour (last element in list)
   

def fetch_live_data():
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": 19.0760,
        "longitude": 72.8777,
        "hourly": "pm2_5,pm10",
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    data = response.json()

    # list of timestamps from API
    times = data["hourly"]["time"]
    now = datetime.now().strftime("%Y-%m-%dT%H:00")

    # find index of current hour
    if now in times:
        i = times.index(now)
    else:
        i = -1  # fallback

    entry = {
        "timestamp": times[i],
        "pm2_5": data["hourly"]["pm2_5"][i],
        "pm10": data["hourly"]["pm10"][i]
    }

    return entry


    entry = {
        "timestamp": data["hourly"]["time"][i],
        "pm2_5": data["hourly"]["pm2_5"][i],
        "pm10": data["hourly"]["pm10"][i],
    }
    return entry


def classify_risk(entry):
    def log_to_csv(entry):
     df = pd.DataFrame([entry])
     file_path = os.path.join("data", "realtime_log.csv")
     header = not os.path.exists(file_path)  # write header only first time
     df.to_csv(file_path, mode="a", header=header, index=False)

    pm2_5 = entry["pm2_5"]

    if pm2_5 <= 30:
        risk = "Low"
        alert = "✅ Air quality is good."
    elif pm2_5 <= 60:
        risk = "Moderate"
        alert = "🟡 Mild pollution. Sensitive groups should be cautious."
    elif pm2_5 <= 90:
        risk = "High"
        alert = "🟠 Unhealthy for sensitive groups."
    else:
        risk = "Very High"
        alert = "⚠️ Unhealthy. Avoid prolonged exposure."

    return risk, alert

def log_to_csv(entry):
    """Save each reading into a CSV file."""
    df = pd.DataFrame([entry])
    file_path = os.path.join("data", "realtime_log.csv")

    # Write header only the first time
    header = not os.path.exists(file_path)

    df.to_csv(file_path, mode="a", header=header, index=False)



@app.route("/data")
def get_data():
    # 1) Get live readings
    entry = fetch_live_data()

    # 2) Add risk + alert
    risk, alert = classify_risk(entry)
    entry["risk"] = risk
    entry["alert"] = alert

    # 3) Log this entry to CSV
    log_to_csv(entry)

    # 4) Return JSON
    return jsonify(entry)


@app.route("/api/data", methods=["POST"])
def receive_esp32_data():
    """Receive sensor data from ESP32 and store it."""
    try:
        data = request.get_json()
        
        # Validate incoming data
        required_fields = ["dust", "temp", "tvoc", "eco2"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Add timestamp
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dust": float(data["dust"]),
            "temp": float(data["temp"]),
            "tvoc": int(data["tvoc"]),
            "eco2": int(data["eco2"])
        }
        
        # Classify risk based on sensor readings
        risk, alert = classify_sensor_risk(entry)
        entry["risk"] = risk
        entry["alert"] = alert
        
        # Log to sensor CSV
        log_sensor_data(entry)
        
        return jsonify({"status": "success", "message": "Data received", "risk": risk}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def classify_sensor_risk(entry):
    """Classify risk based on all sensor readings."""
    dust = entry["dust"]
    temp = entry["temp"]
    tvoc = entry["tvoc"]
    eco2 = entry["eco2"]
    
    risk_score = 0
    alerts = []
    
    # Dust analysis
    if dust > 1000:
        risk_score += 3
        alerts.append("⚠️ CRITICAL: Very high dust concentration!")
    elif dust > 500:
        risk_score += 2
        alerts.append("🟠 High dust levels detected")
    elif dust > 200:
        risk_score += 1
        alerts.append("🟡 Moderate dust levels")
    
    # Temperature analysis
    if temp > 40:
        risk_score += 3
        alerts.append("⚠️ CRITICAL: Temperature too high!")
    elif temp > 35:
        risk_score += 2
        alerts.append("🟠 High temperature detected")
    elif temp > 30:
        risk_score += 1
        alerts.append("🟡 Elevated temperature")
    
    # TVOC analysis
    if tvoc > 500:
        risk_score += 3
        alerts.append("⚠️ CRITICAL: Very high TVOC levels!")
    elif tvoc > 250:
        risk_score += 2
        alerts.append("🟠 High TVOC detected")
    elif tvoc > 100:
        risk_score += 1
        alerts.append("🟡 Moderate TVOC levels")
    
    # eCO2 analysis
    if eco2 > 1000:
        risk_score += 3
        alerts.append("⚠️ CRITICAL: Very high CO2 levels!")
    elif eco2 > 800:
        risk_score += 2
        alerts.append("🟠 High CO2 detected")
    elif eco2 > 600:
        risk_score += 1
        alerts.append("🟡 Moderate CO2 levels")
    
    # Determine overall risk
    if risk_score >= 8:
        risk = "Critical"
        alert_msg = " | ".join(alerts) if alerts else "⚠️ CRITICAL: Multiple hazardous conditions detected!"
    elif risk_score >= 5:
        risk = "High"
        alert_msg = " | ".join(alerts) if alerts else "🟠 High risk environment"
    elif risk_score >= 2:
        risk = "Moderate"
        alert_msg = " | ".join(alerts) if alerts else "🟡 Moderate air quality concerns"
    else:
        risk = "Low"
        alert_msg = "✅ Air quality is good"
    
    return risk, alert_msg


def log_sensor_data(entry):
    """Save sensor readings to CSV file."""
    df = pd.DataFrame([entry])
    file_path = os.path.join("data", "sensor_log.csv")
    
    # Write header only the first time
    header = not os.path.exists(file_path)
    df.to_csv(file_path, mode="a", header=header, index=False)


@app.route("/api/sensor-data")
def get_sensor_data():
    """Get all sensor data for dashboard."""
    try:
        file_path = os.path.join("data", "sensor_log.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Get last 100 readings
            df_recent = df.tail(100)
            return jsonify(df_recent.to_dict(orient="records"))
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/latest-sensor")
def get_latest_sensor():
    """Get latest sensor reading."""
    try:
        file_path = os.path.join("data", "sensor_log.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            latest = df.iloc[-1].to_dict()
            return jsonify(latest)
        else:
            return jsonify({"error": "No data available"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
