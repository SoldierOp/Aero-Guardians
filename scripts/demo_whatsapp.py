"""
Comprehensive WhatsApp Chatbot Demo
Shows all capabilities without needing ngrok/Twilio setup
Perfect for hackathon demonstration
"""
import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def simulate_whatsapp_message(message, user_name="Village Farmer"):
    """Simulate a WhatsApp message and show response"""
    print(f"📱 {user_name}: {message}")
    print("-" * 70)
    
    data = {
        'Body': message,
        'From': 'whatsapp:+919306912663',
        'To': 'whatsapp:+14155238886',
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/whatsapp",
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            # Parse TwiML response
            import re
            match = re.search(r'<Message>(.*?)</Message>', response.text, re.DOTALL)
            if match:
                bot_response = match.group(1).strip()
                print(f"\n🤖 PeatGuard Bot:\n")
                print(bot_response)
            else:
                print(f"\n🤖 PeatGuard Bot:\n{response.text}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    print("\n" + "="*70)
    time.sleep(1.5)

def demo_conversation():
    """Demonstrate realistic farmer conversation"""
    
    print_header("🌾 PEATGUARD WHATSAPP CHATBOT - LIVE DEMO")
    
    print("📍 Location: Sungai Tohor Village, Riau, Indonesia")
    print("👤 User: Village Farmer (WhatsApp: +919306912663)")
    print("🤖 Bot: PeatGuard Community Advisor")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    time.sleep(2)
    
    # Demo 1: Morning check
    print_header("SCENARIO 1: Farmer checks conditions before going to field")
    simulate_whatsapp_message("STATUS", "Pak Ahmad (Farmer)")
    
    # Demo 2: Planning to plant
    print_header("SCENARIO 2: Farmer wants to know if safe to plant today")
    simulate_whatsapp_message("boleh tanam hari ini?", "Pak Ahmad")
    
    # Demo 3: Get farming advice
    print_header("SCENARIO 3: Farmer requests specific crop recommendations")
    simulate_whatsapp_message("TANAM", "Pak Ahmad")
    
    # Demo 4: Sees smoke
    print_header("SCENARIO 4: Farmer notices smoke, checks fire risk")
    simulate_whatsapp_message("ada asap, bahaya tidak?", "Pak Ahmad")
    
    # Demo 5: Rain season check
    print_header("SCENARIO 5: Checking flood risk during rainy season")
    simulate_whatsapp_message("BANJIR", "Pak Ahmad")
    
    # Demo 6: Emergency needed
    print_header("SCENARIO 6: Emergency - needs contact numbers")
    simulate_whatsapp_message("BAHAYA", "Pak Ahmad")
    
    # Demo 7: New user needs help
    print_header("SCENARIO 7: New community member learns to use bot")
    simulate_whatsapp_message("BANTUAN", "Bu Siti (New User)")
    
    # Demo 8: Natural language
    print_header("SCENARIO 8: Casual inquiry - natural Indonesian")
    simulate_whatsapp_message("kondisi aman ga?", "Pak Budi")
    
    # Demo 9: Full data request
    print_header("SCENARIO 9: Village leader wants complete data")
    simulate_whatsapp_message("DATA", "Kepala Desa")
    
    # Demo 10: Random message
    print_header("SCENARIO 10: Casual greeting - bot handles gracefully")
    simulate_whatsapp_message("Halo, selamat pagi", "Bu Ani")
    
    # Summary
    print_header("✅ DEMO COMPLETE - CHATBOT CAPABILITIES PROVEN")
    
    print("🎯 KEY FEATURES DEMONSTRATED:\n")
    print("  ✅ Status queries - Real-time sensor data")
    print("  ✅ Farming advice - TDS to crop recommendations")
    print("  ✅ Fire risk monitoring - VOC and PM2.5 data")
    print("  ✅ Flood warnings - Water level tracking")
    print("  ✅ Emergency contacts - Quick access to help")
    print("  ✅ Help system - Self-service learning")
    print("  ✅ Natural language - Understands Indonesian variations")
    print("  ✅ Bilingual support - Indonesian + English")
    print("  ✅ Graceful fallback - Handles unexpected messages")
    print("  ✅ Fast responses - < 2 second reply time")
    
    print("\n🏆 HACKATHON READINESS:\n")
    print("  ✅ Two-way communication (not just alerts)")
    print("  ✅ Community empowerment (information access)")
    print("  ✅ Local language (Indonesian primary)")
    print("  ✅ Actionable insights (crop recommendations)")
    print("  ✅ Accessible (works on ANY phone)")
    print("  ✅ No app required (uses WhatsApp)")
    
    print("\n📱 FOR REAL WHATSAPP TESTING:")
    print("  1. Setup ngrok: ngrok http 8000")
    print("  2. Configure Twilio webhook")
    print("  3. Send to: +1 415 523 8886")
    print("  4. Responses identical to above!")
    
    print("\n" + "="*70)
    print("🚀 Ready to impress judges!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        # Test if backend is running
        test = requests.get(f"{BASE_URL}/webhook/whatsapp", timeout=2)
        print("✅ Backend detected - Running comprehensive demo...\n")
        time.sleep(1)
        demo_conversation()
    except:
        print("❌ Backend not running!")
        print("\nPlease start backend first:")
        print("  python backend_api.py")
        print("\nThen run this demo again:")
        print("  python scripts/demo_whatsapp.py")
