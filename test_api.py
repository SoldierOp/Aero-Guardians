import requests
import json
import random
import time

# Test data endpoint
API_URL = "http://127.0.0.1:5000/api/data"

def generate_test_data():
    """Generate realistic sensor data for testing."""
    return {
        "dust": round(random.uniform(50, 800), 2),
        "temp": round(random.uniform(20, 35), 2),
        "tvoc": random.randint(20, 400),
        "eco2": random.randint(400, 900)
    }

def test_single_post():
    """Send a single test reading."""
    data = generate_test_data()
    
    print("\n" + "="*50)
    print("Testing ESP32 API Endpoint")
    print("="*50)
    print(f"\nSending test data:")
    print(json.dumps(data, indent=2))
    
    try:
        response = requests.post(API_URL, json=data, timeout=5)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.json()}")
        
        if response.status_code == 200:
            print("\n✓ SUCCESS! API is working correctly!")
            return True
        else:
            print(f"\n✗ ERROR: Unexpected status code")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to Flask backend")
        print("Make sure Flask is running: python app.py")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        return False

def continuous_test(count=10, interval=2):
    """Send multiple test readings."""
    print(f"\nSending {count} test readings (every {interval}s)...")
    print("This will populate your dashboard with test data")
    print("Press Ctrl+C to stop\n")
    
    successful = 0
    failed = 0
    
    try:
        for i in range(count):
            data = generate_test_data()
            
            print(f"[{i+1}/{count}] Dust={data['dust']:.1f} Temp={data['temp']:.1f} TVOC={data['tvoc']} eCO2={data['eco2']}", end=" ... ")
            
            try:
                response = requests.post(API_URL, json=data, timeout=5)
                if response.status_code == 200:
                    print("✓ OK")
                    successful += 1
                else:
                    print(f"✗ FAIL ({response.status_code})")
                    failed += 1
            except Exception as e:
                print(f"✗ ERROR")
                failed += 1
            
            if i < count - 1:  # Don't sleep after last one
                time.sleep(interval)
                
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    print(f"\n{'='*50}")
    print(f"Results: {successful} successful, {failed} failed")
    print(f"{'='*50}")

def test_get_endpoints():
    """Test the GET endpoints."""
    print("\n" + "="*50)
    print("Testing GET Endpoints")
    print("="*50)
    
    # Test latest sensor
    print("\n1. Testing /api/latest-sensor...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/latest-sensor", timeout=5)
        if response.status_code == 200:
            print("✓ Latest sensor data:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"✗ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test all sensor data
    print("\n2. Testing /api/sensor-data...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/sensor-data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data)} sensor readings")
            if len(data) > 0:
                print(f"Latest reading: {data[-1]}")
        else:
            print(f"✗ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("="*50)
    print("  AeroGuardians - API Test Suite")
    print("="*50)
    print("\nOptions:")
    print("1. Send single test reading")
    print("2. Send multiple test readings (populate dashboard)")
    print("3. Test GET endpoints")
    print("4. Run all tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        test_single_post()
    elif choice == "2":
        count = input("How many readings? (default 10): ").strip()
        count = int(count) if count else 10
        continuous_test(count)
    elif choice == "3":
        test_get_endpoints()
    elif choice == "4":
        if test_single_post():
            continuous_test(5, 1)
            test_get_endpoints()
    else:
        print("Invalid choice!")
    
    print("\n" + "="*50)
    print("Test complete! Check your dashboard for results.")
    print("="*50)
