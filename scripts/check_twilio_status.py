"""
Check Twilio Message Status
Retrieves detailed status of the last sent message
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

def check_message_status(message_sid):
    """Check the status of a specific message"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages(message_sid).fetch()
        
        print(f"📊 Message Status Report")
        print(f"   SID: {message.sid}")
        print(f"   Status: {message.status}")
        print(f"   From: {message.from_}")
        print(f"   To: {message.to}")
        print(f"   Date Created: {message.date_created}")
        print(f"   Date Updated: {message.date_updated}")
        print(f"   Error Code: {message.error_code}")
        print(f"   Error Message: {message.error_message}")
        print()
        
        # Status meanings
        status_meanings = {
            'queued': '⏳ Message is waiting to be sent',
            'sent': '✅ Message was sent (but not delivered yet)',
            'delivered': '✅ Message was delivered successfully',
            'failed': '❌ Message failed to send',
            'undelivered': '❌ Message could not be delivered',
            'receiving': '📥 Message is being received',
            'received': '✅ Message was received'
        }
        
        print(f"💡 Status Meaning: {status_meanings.get(message.status, 'Unknown')}")
        
        if message.error_code:
            print(f"\n❌ ERROR DETECTED!")
            print(f"   Code: {message.error_code}")
            print(f"   Message: {message.error_message}")
            print(f"\n🔍 Common Error Codes:")
            print(f"   21408: Permission to send to unverified number")
            print(f"   63016: Recipient not in sandbox or not verified")
            print(f"   63007: Sandbox join expired (needs rejoin)")
        
        return message.status
        
    except Exception as e:
        print(f"❌ Error checking message status: {e}")
        return None

def list_recent_messages():
    """List recent messages from your account"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        messages = client.messages.list(limit=5)
        
        print(f"\n📜 Recent Messages (last 5):")
        print("=" * 70)
        
        for msg in messages:
            status_emoji = {
                'delivered': '✅',
                'sent': '📤',
                'queued': '⏳',
                'failed': '❌',
                'undelivered': '❌'
            }.get(msg.status, '❓')
            
            print(f"{status_emoji} {msg.sid}")
            print(f"   To: {msg.to}")
            print(f"   Status: {msg.status}")
            print(f"   Created: {msg.date_created}")
            if msg.error_code:
                print(f"   ❌ Error {msg.error_code}: {msg.error_message}")
            print()
        
    except Exception as e:
        print(f"❌ Error listing messages: {e}")

if __name__ == "__main__":
    print("=" * 70)
    print("  Twilio Message Status Check")
    print("=" * 70)
    print()
    
    # Check the specific message we just sent (latest attempt)
    message_sid = "SM6e6c7cfb9623b7b6383fcf5eb15a42eb"
    
    print(f"🔍 Checking message: {message_sid}")
    print()
    
    check_message_status(message_sid)
    
    # List all recent messages for context
    list_recent_messages()
    
    print("=" * 70)
