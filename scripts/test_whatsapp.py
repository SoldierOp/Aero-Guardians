"""
Test WhatsApp Alert System
Sends a test flood alert to verify Twilio integration
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

# Your WhatsApp number
TEST_RECIPIENT = 'whatsapp:+919306912663'

def send_test_alert():
    """Send a test WhatsApp alert"""
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("❌ Error: Missing Twilio credentials in .env file")
        return False
    
    print(f"🔧 Testing WhatsApp with Twilio...")
    print(f"   Account SID: {TWILIO_ACCOUNT_SID[:10]}...")
    print(f"   From: {TWILIO_WHATSAPP_FROM}")
    print(f"   To: {TEST_RECIPIENT}")
    print()
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Test message
        message = """
🚨 *TEST ALERT - PeatSense*

This is a test message from your PeatSense system.

If you received this, WhatsApp alerts are working! ✅

System: PeatSense Peatland Monitoring
Location: Sungai Tohor, Indonesia
Status: Test Mode

---
To stop test messages, close this script.
        """.strip()
        
        print("📤 Sending test message...")
        
        msg = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=TEST_RECIPIENT
        )
        
        print(f"✅ SUCCESS! Message sent")
        print(f"   Message SID: {msg.sid}")
        print(f"   Status: {msg.status}")
        print()
        print(f"📱 Check your WhatsApp at {TEST_RECIPIENT}")
        print(f"   You should receive the message in 1-5 seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED to send WhatsApp message")
        print(f"   Error: {e}")
        print()
        print("Common issues:")
        print("  1. Did you join the sandbox? Send 'join author-to' to +1 415 523 8886")
        print("  2. Check your credentials in .env file")
        print("  3. Verify your Twilio account is active")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  PeatSense WhatsApp Test")
    print("=" * 60)
    print()
    
    send_test_alert()
    
    print()
    print("=" * 60)
