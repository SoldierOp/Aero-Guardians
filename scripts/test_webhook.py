"""
Simulate WhatsApp webhook for testing
"""
import requests
import time

# Your local backend URL
BASE_URL = "http://localhost:8000"

def test_webhook(message):
    """Simulate Twilio webhook POST"""
    print(f"\n{'='*60}")
    print(f"📱 Sending: {message}")
    print('='*60)
    
    # Simulate Twilio's form data
    data = {
        'Body': message,
        'From': 'whatsapp:+919306912663',
        'To': 'whatsapp:+14155238886',
        'MessageSid': f'TEST{int(time.time())}',
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/whatsapp",
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"\n🤖 Bot Response:\n")
        # Parse TwiML response
        if '<Message>' in response.text:
            import re
            match = re.search(r'<Message>(.*?)</Message>', response.text, re.DOTALL)
            if match:
                print(match.group(1).strip())
        else:
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🤖 WHATSAPP CHATBOT WEBHOOK TEST")
    print("Testing chatbot with simulated Twilio webhook...")
    
    # Test various commands
    test_messages = [
        "STATUS",
        "TANAM",
        "BANTUAN",
        "kondisi aman?",
    ]
    
    for msg in test_messages:
        test_webhook(msg)
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print("✅ Test complete! If you see responses above, chatbot works!")
    print(f"{'='*60}")
