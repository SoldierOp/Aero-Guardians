#!/usr/bin/env python3
"""
PeatGuard Sensor Diagnostic Tool
Tests which sensors are reporting data to the backend API

Usage:
    python test_sensor_status.py
"""

import sys
import time
import requests
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

# Configuration
BACKEND_URL = "http://localhost:8000"
API_TIMEOUT = 5  # seconds

def print_header():
    """Print test header"""
    print("\n" + "="*60)
    print(f"{Fore.CYAN}🔬 PeatGuard Sensor Diagnostic Tool{Style.RESET_ALL}")
    print(f"   Testing sensor data reception")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

def check_backend_health():
    """Check if backend API is running"""
    print(f"{Fore.YELLOW}⏳ Checking backend API...{Style.RESET_ALL}")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=API_TIMEOUT)
        if response.status_code == 200:
            print(f"{Fore.GREEN}✅ Backend API is running{Style.RESET_ALL}")
            print(f"   URL: {BACKEND_URL}")
            return True
        else:
            print(f"{Fore.RED}❌ Backend API returned error: {response.status_code}{Style.RESET_ALL}")
            return False
    except requests.ConnectionError:
        print(f"{Fore.RED}❌ Cannot connect to backend at {BACKEND_URL}{Style.RESET_ALL}")
        print(f"   Make sure backend_api.py is running!")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error checking backend: {e}{Style.RESET_ALL}")
        return False

def get_latest_sensor_data():
    """Retrieve the latest sensor data from API"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/sensor-data/latest",
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"{Fore.YELLOW}⚠️  No sensor data received yet{Style.RESET_ALL}")
            return None
        else:
            print(f"{Fore.RED}❌ API error: {response.status_code}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}❌ Error fetching data: {e}{Style.RESET_ALL}")
        return None

def analyze_sensor_data(data):
    """Analyze sensor data and report status"""
    if not data:
        print(f"\n{Fore.YELLOW}⚠️  No sensor data available to analyze{Style.RESET_ALL}")
        print(f"   Make sure ESP32 is:")
        print(f"   1. Powered on")
        print(f"   2. Connected to WiFi")
        print(f"   3. Publishing to MQTT/API")
        return
    
    print(f"\n{Fore.CYAN}📊 Sensor Status Report{Style.RESET_ALL}")
    print("-" * 60)
    
    # Expected sensor fields
    sensors = {
        "🔥 VOC (SGP30)": {
            "fields": ["voc", "tvoc", "eco2"],
            "units": "ppb/ppm",
            "normal_range": "0-60000 ppb"
        },
        "🌡️  Temperature": {
            "fields": ["temperature", "temp"],
            "units": "°C",
            "normal_range": "15-45°C"
        },
        "💧 Humidity": {
            "fields": ["humidity", "hum"],
            "units": "%",
            "normal_range": "20-100%"
        },
        "💨 PM2.5 (Dust)": {
            "fields": ["pm25", "pm2_5", "dust_pm25"],
            "units": "µg/m³",
            "normal_range": "0-500 µg/m³"
        },
        "🔬 PM1.0 (PMS5003)": {
            "fields": ["pm10", "pm1_0", "pms_pm10"],
            "units": "µg/m³",
            "normal_range": "0-500 µg/m³"
        },
        "🔬 PM10 (PMS5003)": {
            "fields": ["pm100", "pm10_0", "pms_pm100"],
            "units": "µg/m³",
            "normal_range": "0-1000 µg/m³"
        },
        "💧 TDS (Salinity)": {
            "fields": ["tds", "salinity"],
            "units": "ppm",
            "normal_range": "0-2000 ppm"
        },
        "🌊 Water Level": {
            "fields": ["water_level", "water", "ultrasonic"],
            "units": "cm",
            "normal_range": "0-400 cm"
        }
    }
    
    working_count = 0
    missing_count = 0
    
    for sensor_name, config in sensors.items():
        found = False
        value = None
        field_name = None
        
        # Check if any field variant exists in data
        for field in config["fields"]:
            if field in data:
                found = True
                value = data[field]
                field_name = field
                break
        
        if found and value is not None:
            print(f"{Fore.GREEN}✅ {sensor_name}: {value} {config['units']}{Style.RESET_ALL}")
            print(f"   Field: '{field_name}' | Range: {config['normal_range']}")
            working_count += 1
        else:
            print(f"{Fore.RED}❌ {sensor_name}: NOT REPORTING{Style.RESET_ALL}")
            print(f"   Missing fields: {', '.join(config['fields'])}")
            missing_count += 1
    
    print("-" * 60)
    print(f"\n{Fore.CYAN}📈 Summary:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}✅ Working: {working_count}{Style.RESET_ALL}")
    print(f"   {Fore.RED}❌ Missing: {missing_count}{Style.RESET_ALL}")
    print(f"   {Fore.YELLOW}📡 Total fields in data: {len(data)}{Style.RESET_ALL}")
    
    # Show timestamp if available
    if "timestamp" in data:
        print(f"   🕐 Last update: {data['timestamp']}")
    
    # Show all received fields
    print(f"\n{Fore.CYAN}📋 All received fields:{Style.RESET_ALL}")
    for key, value in data.items():
        if key not in ["id", "timestamp", "node_id"]:
            print(f"   • {key}: {value}")

def wait_for_new_data(duration=30):
    """Wait for new sensor data to arrive"""
    print(f"\n{Fore.YELLOW}⏳ Waiting {duration} seconds for new sensor data...{Style.RESET_ALL}")
    print(f"   (Data should arrive every 30-60 seconds)")
    
    for i in range(duration):
        print(f"\r   Waiting: {duration - i} seconds remaining...", end="", flush=True)
        time.sleep(1)
    
    print("\n")

def main():
    """Main diagnostic routine"""
    print_header()
    
    # Step 1: Check backend
    if not check_backend_health():
        print(f"\n{Fore.RED}❌ Backend is not running. Start it with:{Style.RESET_ALL}")
        print(f"   python backend_api.py")
        print(f"   or")
        print(f"   start_backend.bat")
        sys.exit(1)
    
    print("")
    
    # Step 2: Get latest data
    print(f"{Fore.YELLOW}📡 Fetching latest sensor data...{Style.RESET_ALL}")
    data = get_latest_sensor_data()
    
    if not data:
        # Wait for data to arrive
        wait_for_new_data(30)
        data = get_latest_sensor_data()
    
    # Step 3: Analyze
    analyze_sensor_data(data)
    
    # Step 4: Recommendations
    print(f"\n{Fore.CYAN}💡 Recommendations:{Style.RESET_ALL}")
    if data and len(data) >= 6:
        print(f"{Fore.GREEN}✅ Most sensors are reporting - system looks healthy!{Style.RESET_ALL}")
        print(f"   Next: Test alerts with scripts/test_whatsapp.py")
    elif data and len(data) >= 3:
        print(f"{Fore.YELLOW}⚠️  Some sensors missing - check wiring{Style.RESET_ALL}")
        print(f"   1. Upload: test_connected_sensors/test_connected_sensors.ino")
        print(f"   2. Check Serial Monitor for sensor errors")
        print(f"   3. Review: SENSOR_TEST_GUIDE.md")
    else:
        print(f"{Fore.RED}❌ Few/no sensors reporting - hardware issue{Style.RESET_ALL}")
        print(f"   1. Verify ESP32 is powered on")
        print(f"   2. Check WiFi connection")
        print(f"   3. Upload test firmware: test_connected_sensors.ino")
        print(f"   4. Open Serial Monitor (115200 baud)")
        print(f"   5. Follow troubleshooting in SENSOR_TEST_GUIDE.md")
    
    print("\n" + "="*60)
    print(f"{Fore.CYAN}Test complete!{Style.RESET_ALL}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Test interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
