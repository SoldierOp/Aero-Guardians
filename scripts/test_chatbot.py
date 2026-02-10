"""
Quick test script for WhatsApp Chatbot
Tests the chatbot logic without needing Twilio webhook
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock sensor data for testing
class MockSensorData:
    def __init__(self):
        self.data = {
            'node_id': 'SungaiTohor_Node01',
            'timestamp': 1707177600,  # Feb 6, 2026
            'water_level': 85.0,
            'tds': 450.0,
            'voc': 350,
            'pm25': 25,
            'pm10': 35,
            'temperature': 28.5,
            'humidity': 75.0,
            'fire_risk': 0,  # 0=SAFE, 1=WARNING, 2=DANGER
            'flood_risk': 0,
            'overall_risk': 0
        }

def get_mock_sensor_data(node_id="SungaiTohor_Node01"):
    """Mock function to replace database query"""
    return MockSensorData().data

def get_crop_recommendation(tds: float, water_level: float):
    """Convert sensor data to farming advice"""
    if tds < 500:
        salinity_status = "AIR TAWAR - AMAN"
        crops_ok = ["Padi", "Sayuran", "Jagung"]
        crops_avoid = []
    elif tds < 1500:
        salinity_status = "SEDIKIT ASIN - HATI-HATI"
        crops_ok = ["Padi tahan garam", "Rumput pakan ternak"]
        crops_avoid = ["Sayuran sensitif"]
    else:
        salinity_status = "AIR ASIN - BAHAYA"
        crops_ok = ["Rumput laut", "Bakau"]
        crops_avoid = ["Padi", "Jagung", "Sayuran"]
    
    if water_level > 180:
        flood_advice = "⚠️ Risiko banjir TINGGI - Tunda penanaman, siapkan evakuasi"
    elif water_level > 120:
        flood_advice = "⚠️ Risiko banjir SEDANG - Gunakan varietas cepat panen (60 hari)"
    else:
        flood_advice = "✅ Aman untuk menanam musim penuh"
    
    return {
        "salinity": salinity_status,
        "crops_ok": crops_ok,
        "crops_avoid": crops_avoid,
        "flood_advice": flood_advice
    }

def process_chatbot_message(incoming_msg: str):
    """Test the chatbot logic"""
    from datetime import datetime
    
    msg_upper = incoming_msg.strip().upper()
    sensor_data = get_mock_sensor_data()
    
    if not sensor_data:
        return "⚠️ Maaf, sistem sedang offline."
    
    last_update = datetime.fromtimestamp(sensor_data['timestamp'])
    time_diff = datetime.now() - last_update
    minutes_ago = int(time_diff.total_seconds() / 60)
    
    # STATUS QUERY
    if "STATUS" in msg_upper or "AMAN" in msg_upper or "KONDISI" in msg_upper:
        fire_level = ["AMAN ✅", "HATI-HATI ⚠️", "BAHAYA 🚨"][sensor_data['fire_risk']]
        flood_level = ["AMAN ✅", "HATI-HATI ⚠️", "BAHAYA 🚨"][sensor_data['flood_risk']]
        
        response = f"""📊 *STATUS PEATGUARD*

🌊 Ketinggian Air: {sensor_data['water_level']:.0f} cm ({flood_level})
🔥 Risiko Api: {fire_level}
🧂 Salinitas: {sensor_data['tds']:.0f} ppm
🌡️ Suhu: {sensor_data['temperature']:.1f}°C
💧 Kelembaban: {sensor_data['humidity']:.0f}%

⏱️ Update: {minutes_ago} menit lalu

Kirim 'TANAM' untuk saran pertanian
Kirim 'BAHAYA' untuk kontak darurat"""
        return response
    
    # FARMING ADVICE
    elif "TANAM" in msg_upper:
        rec = get_crop_recommendation(sensor_data['tds'], sensor_data['water_level'])
        crops_ok_str = ", ".join(rec['crops_ok'])
        crops_avoid_str = ", ".join(rec['crops_avoid']) if rec['crops_avoid'] else "Tidak ada"
        
        response = f"""🌾 *REKOMENDASI PERTANIAN*

🧂 Status Air: {rec['salinity']}
✅ Cocok tanam: {crops_ok_str}
❌ Hindari: {crops_avoid_str}

{rec['flood_advice']}

📊 Data: Garam {sensor_data['tds']:.0f}ppm, Air {sensor_data['water_level']:.0f}cm

Kirim 'STATUS' untuk kondisi terkini"""
        return response
    
    # HELP MENU
    elif "BANTUAN" in msg_upper or "HELP" in msg_upper:
        return """ℹ️ *MENU PEATGUARD BOT*

📊 Kirim 'STATUS' → Kondisi terkini
🌾 Kirim 'TANAM' → Saran pertanian
🔥 Kirim 'API' → Info risiko kebakaran
🌊 Kirim 'BANJIR' → Info risiko banjir
🚨 Kirim 'BAHAYA' → Kontak darurat
📈 Kirim 'DATA' → Data lengkap sensor

💬 Tanya apa saja tentang kondisi lahan gambut!"""
    
    else:
        return f"""👋 Terima kasih pesan Anda!

Saya PeatGuard Bot, siap membantu monitoring lahan gambut.

💡 Coba kirim:
• 'STATUS' - Cek kondisi sekarang
• 'TANAM' - Saran pertanian
• 'BANTUAN' - Lihat menu lengkap

📊 Kondisi saat ini:
🌊 Air: {sensor_data['water_level']:.0f}cm
🔥 Risiko: {['Aman','Waspada','Bahaya'][sensor_data['fire_risk']]}"""

def test_chatbot():
    """Run test queries"""
    print("=" * 60)
    print("🤖 WHATSAPP CHATBOT TEST")
    print("=" * 60)
    
    test_messages = [
        "STATUS",
        "TANAM",
        "BANTUAN",
        "kondisi aman?",
        "Hello",
    ]
    
    for msg in test_messages:
        print(f"\n📱 User: {msg}")
        print("-" * 60)
        response = process_chatbot_message(msg)
        print(f"🤖 Bot:\n{response}")
        print("=" * 60)

if __name__ == "__main__":
    test_chatbot()
