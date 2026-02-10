"""
Quick test script for PeatSense backend API
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_create_reading():
    """Test creating a sensor reading"""
    print("Testing POST /api/readings...")
    
    data = {
        "node_id": "test_node_001",
        "timestamp": 1704672000000,
        "water_level": 125.5,
        "tds": 450.0,
        "voc": 380,
        "eco2": 420,
        "pm25": 45,
        "temperature": 28.5,
        "humidity": 78.0,
        "flood_risk": 0,
        "fire_risk": 0,
        "overall_risk": 0,
        "lat": 0.8512,
        "lon": 103.3556
    }
    
    response = requests.post(f"{API_BASE}/readings", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_dashboard_stats():
    """Test dashboard stats endpoint"""
    print("Testing /api/dashboard/stats...")
    response = requests.get(f"{API_BASE}/dashboard/stats")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Total Nodes: {stats.get('total_nodes', 0)}")
        print(f"Active Nodes: {stats.get('active_nodes', 0)}")
        print(f"Nodes in Warning: {stats.get('nodes_in_warning', 0)}")
        print(f"Nodes in Danger: {stats.get('nodes_in_danger', 0)}")
    else:
        print(f"Response: {response.text}")
    print()

def test_create_alert():
    """Test creating an alert"""
    print("Testing POST /api/alerts...")
    
    data = {
        "node_id": "test_node_001",
        "type": "FLOOD",
        "level": "WARNING",
        "message": "Test alert - water level rising",
        "water_level": 155.0,
        "tds": 850.0
    }
    
    response = requests.post(f"{API_BASE}/alerts", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("PeatSense Backend API Test")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_create_reading()
        test_dashboard_stats()
        # test_create_alert()  # Uncomment to test alerts
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend.")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
