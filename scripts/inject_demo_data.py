"""
Inject demo sensor data directly into backend for chatbot testing
(Bypasses database - stores in memory for demo)
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api"

def create_demo_reading():
    """Create a realistic demo sensor reading"""
    
    # Current timestamp
    current_timestamp = int(datetime.now().timestamp())
    
    data = {
        "node_id": "SungaiTohor_Node01",
        "timestamp": current_timestamp,
        "water_level": 85.0,
        "water_present": 1,
        "tds": 450.0,
        "voc": 350,
        "eco2": 420,
        "pm1_0": 15,
        "pm25": 25,
        "pm10": 35,
        "dust_concentration": 0,
        "temperature": 28.5,
        "humidity": 75.0,
        "flood_risk": 0,  # 0=SAFE, 1=WARNING, 2=DANGER
        "fire_risk": 0,
        "overall_risk": 0,
        "lat": 0.8512,
        "lon": 103.3556
    }
    
    print("📊 Sending demo sensor data to backend...")
    print(f"Node: {data['node_id']}")
    print(f"Timestamp: {datetime.fromtimestamp(current_timestamp)}")
    print(f"Water Level: {data['water_level']} cm")
    print(f"TDS: {data['tds']} ppm")
    print(f"VOC: {data['voc']} ppb")
    print(f"PM2.5: {data['pm25']} µg/m³")
    print()
    
    try:
        response = requests.post(f"{API_BASE}/readings", json=data)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Demo data injected successfully!")
            print()
            print("Now test chatbot:")
            print("  python scripts/test_webhook.py")
            print()
            print("Or with real WhatsApp:")
            print("  1. Start ngrok: ngrok http 8000")
            print("  2. Configure Twilio webhook")
            print("  3. Send 'STATUS' to WhatsApp")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure backend is running:")
        print("  python backend_api.py")

if __name__ == "__main__":
    create_demo_reading()
