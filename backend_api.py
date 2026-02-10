"""
PeatSense Backend API
FastAPI-based backend for peatland groundwater monitoring

Features:
- MQTT broker integration for IoT data ingestion
- PostgreSQL time-series storage
- WhatsApp alert system (Twilio/WABA)
- Risk calculation and alert engine
- RESTful API for dashboard

Author: PeatSense Team
Version: 1.0
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import paho.mqtt.client as mqtt
import json
import os
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import asyncio

# ============= CONFIGURATION =============

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'peatsense'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mqtt.peatsense.local')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_TOPIC_DATA = 'peatsense/data'
MQTT_TOPIC_ALERT = 'peatsense/alerts'

# WhatsApp Configuration (Twilio)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

# Village Leader WhatsApp Numbers
VILLAGE_LEADERS = [
    'whatsapp:+919306912663',  # Your test number
    # Add more numbers as needed
]

# Alert Cooldown (prevent spam) - 60 minutes for important alerts only
ALERT_COOLDOWN_MINUTES = 60

# Only send WhatsApp for DANGER level alerts (not WARNING)
WHATSAPP_DANGER_ONLY = True

# ============= FASTAPI APP =============

app = FastAPI(
    title="PeatSense API",
    description="Backend API for peatland groundwater and fire risk monitoring",
    version="1.0"
)

# CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= DATA MODELS =============

class SensorReading(BaseModel):
    node_id: str
    timestamp: int
    water_level: float
    water_present: int  # Water presence sensor (0 or 1)
    tds: float
    voc: int
    eco2: int
    pm1_0: int  # PM1.0 from PMS5003
    pm25: int   # PM2.5 from PMS5003
    pm10: int   # PM10 from PMS5003
    dust_concentration: int  # Grove Dust Sensor (backup)
    temperature: float
    humidity: float
    flood_risk: int
    fire_risk: int
    overall_risk: int
    lat: float
    lon: float

class AlertData(BaseModel):
    node_id: str
    type: str  # "FLOOD" or "FIRE"
    level: str  # "WARNING" or "DANGER"
    message: str
    water_level: Optional[float] = None
    tds: Optional[float] = None
    voc: Optional[int] = None
    pm25: Optional[int] = None

class DashboardStats(BaseModel):
    total_nodes: int
    active_nodes: int
    nodes_in_danger: int
    nodes_in_warning: int
    latest_readings: List[dict]

# ============= DATABASE FUNCTIONS =============

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create sensor_readings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id SERIAL PRIMARY KEY,
                node_id VARCHAR(50) NOT NULL,
                timestamp BIGINT NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                water_level FLOAT,
                water_present INTEGER,
                tds FLOAT,
                voc INTEGER,
                eco2 INTEGER,
                pm1_0 INTEGER,
                pm25 INTEGER,
                pm10 INTEGER,
                dust_concentration INTEGER,
                temperature FLOAT,
                humidity FLOAT,
                flood_risk INTEGER,
                fire_risk INTEGER,
                overall_risk INTEGER,
                lat FLOAT,
                lon FLOAT
            )
        """)
        
        # Create alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                node_id VARCHAR(50) NOT NULL,
                alert_type VARCHAR(20) NOT NULL,
                alert_level VARCHAR(20) NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_to_whatsapp BOOLEAN DEFAULT FALSE,
                whatsapp_sent_at TIMESTAMP,
                data JSONB
            )
        """)
        
        # Create nodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                node_id VARCHAR(50) PRIMARY KEY,
                location_name VARCHAR(100),
                lat FLOAT,
                lon FLOAT,
                installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active'
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_readings_node_timestamp 
            ON sensor_readings(node_id, timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_created 
            ON alerts(created_at DESC)
        """)
        
        conn.commit()
        cursor.close()
        print("✓ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    finally:
        conn.close()

def store_sensor_reading(reading: SensorReading):
    """Store sensor reading in database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sensor_readings 
            (node_id, timestamp, water_level, water_present, tds, voc, eco2, 
             pm1_0, pm25, pm10, dust_concentration,
             temperature, humidity, flood_risk, fire_risk, overall_risk, lat, lon)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            reading.node_id,
            reading.timestamp,
            reading.water_level,
            reading.water_present,
            reading.tds,
            reading.voc,
            reading.eco2,
            reading.pm1_0,
            reading.pm25,
            reading.pm10,
            reading.dust_concentration,
            reading.temperature,
            reading.humidity,
            reading.flood_risk,
            reading.fire_risk,
            reading.overall_risk,
            reading.lat,
            reading.lon
        ))
        
        # Update node last_seen
        cursor.execute("""
            INSERT INTO nodes (node_id, lat, lon, last_seen)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (node_id) 
            DO UPDATE SET last_seen = CURRENT_TIMESTAMP, lat = %s, lon = %s
        """, (reading.node_id, reading.lat, reading.lon, reading.lat, reading.lon))
        
        conn.commit()
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to store reading: {e}")
        return False
    finally:
        conn.close()

def store_alert(alert: AlertData):
    """Store alert in database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check for recent alerts (cooldown)
        cursor.execute("""
            SELECT created_at FROM alerts 
            WHERE node_id = %s AND alert_type = %s 
            ORDER BY created_at DESC LIMIT 1
        """, (alert.node_id, alert.type))
        
        result = cursor.fetchone()
        if result:
            last_alert_time = result[0]
            time_diff = datetime.now() - last_alert_time
            if time_diff < timedelta(minutes=ALERT_COOLDOWN_MINUTES):
                print(f"⏳ Alert cooldown active for {alert.node_id}")
                return False
        
        # Store new alert
        cursor.execute("""
            INSERT INTO alerts 
            (node_id, alert_type, alert_level, message, data)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            alert.node_id,
            alert.type,
            alert.level,
            alert.message,
            json.dumps(alert.dict())
        ))
        
        alert_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        
        return alert_id
        
    except Exception as e:
        print(f"❌ Failed to store alert: {e}")
        return False
    finally:
        conn.close()

# ============= MQTT FUNCTIONS =============

def on_mqtt_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        print("✓ Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC_DATA)
        client.subscribe(MQTT_TOPIC_ALERT)
    else:
        print(f"❌ MQTT connection failed with code {rc}")

def on_mqtt_message(client, userdata, msg):
    """MQTT message callback"""
    try:
        payload = json.loads(msg.payload.decode())
        
        if msg.topic == MQTT_TOPIC_DATA:
            # Sensor data received
            reading = SensorReading(**payload)
            store_sensor_reading(reading)
            print(f"📊 Stored reading from {reading.node_id}")
            
        elif msg.topic == MQTT_TOPIC_ALERT:
            # Alert received
            alert = AlertData(**payload)
            alert_id = store_alert(alert)
            
            if alert_id:
                print(f"🚨 Alert stored: {alert.type} from {alert.node_id}")
                
                # Send WhatsApp only for DANGER level alerts (important only)
                if not WHATSAPP_DANGER_ONLY or alert.level == "DANGER":
                    asyncio.create_task(send_whatsapp_alert(alert_id, alert))
                    print(f"📱 WhatsApp alert queued for {alert.level} level")
                else:
                    print(f"ℹ️ {alert.level} alert stored but not sent to WhatsApp (danger-only mode)")
            
    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_mqtt_connect
mqtt_client.on_message = on_mqtt_message

# ============= WHATSAPP FUNCTIONS =============

async def send_whatsapp_alert(alert_id: int, alert: AlertData):
    """Send WhatsApp alert to village leaders (important alerts only)"""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("⚠ WhatsApp not configured (missing Twilio credentials)")
        return
    
    # Extra safety: Only send DANGER level alerts
    if WHATSAPP_DANGER_ONLY and alert.level != "DANGER":
        print(f"ℹ️ Skipping WhatsApp for {alert.level} level (danger-only mode)")
        return
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Format message in Indonesian
        if alert.type == "FLOOD":
            message = f"""
🚨 *PERINGATAN BANJIR*

Lokasi: {alert.node_id}
Status: {alert.level}

Ketinggian Air: {alert.water_level:.1f} cm
Salinitas: {alert.tds:.0f} ppm

{alert.message}

Segera koordinasikan evakuasi jika diperlukan.
Salam, PeatSense System
            """.strip()
        else:  # FIRE
            message = f"""
🔥 *PERINGATAN KEBAKARAN*

Lokasi: {alert.node_id}
Status: {alert.level}

Gas VOC: {alert.voc} ppb
Asap (PM2.5): {alert.pm25} µg/m³

{alert.message}

Aktifkan tim pemadam kebakaran desa.
Salam, PeatSense System
            """.strip()
        
        # Send to all village leaders
        success_count = 0
        for recipient in VILLAGE_LEADERS:
            try:
                msg = client.messages.create(
                    body=message,
                    from_=TWILIO_WHATSAPP_FROM,
                    to=recipient
                )
                success_count += 1
                print(f"✓ WhatsApp sent to {recipient}: {msg.sid}")
            except Exception as e:
                print(f"❌ Failed to send to {recipient}: {e}")
        
        # Update alert record
        if success_count > 0:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE alerts 
                    SET sent_to_whatsapp = TRUE, whatsapp_sent_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (alert_id,))
                conn.commit()
                cursor.close()
                conn.close()
        
        print(f"📱 WhatsApp alerts sent: {success_count}/{len(VILLAGE_LEADERS)}")
        
    except Exception as e:
        print(f"❌ WhatsApp send failed: {e}")

# ============= API ENDPOINTS =============

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 PeatSense Backend Starting...")
    
    # Initialize database
    init_database()
    
    # Connect to MQTT broker
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        print("✓ MQTT client started")
    except Exception as e:
        print(f"❌ MQTT connection failed: {e}")
    
    print("✅ Backend ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("👋 Backend shutdown complete")

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "PeatSense API",
        "version": "1.0",
        "status": "operational"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    db_ok = get_db_connection() is not None
    
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "mqtt": "connected" if mqtt_client.is_connected() else "disconnected"
    }

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Count total nodes
        cursor.execute("SELECT COUNT(*) as count FROM nodes WHERE status = 'active'")
        total_nodes = cursor.fetchone()['count']
        
        # Count active nodes (seen in last hour)
        cursor.execute("""
            SELECT COUNT(*) as count FROM nodes 
            WHERE last_seen > NOW() - INTERVAL '1 hour' AND status = 'active'
        """)
        active_nodes = cursor.fetchone()['count']
        
        # Get latest readings with risk levels
        cursor.execute("""
            SELECT DISTINCT ON (node_id)
                node_id, water_level, tds, voc, pm25, temperature,
                flood_risk, fire_risk, overall_risk, 
                recorded_at, lat, lon
            FROM sensor_readings
            ORDER BY node_id, timestamp DESC
            LIMIT 10
        """)
        latest_readings = cursor.fetchall()
        
        # Count nodes in danger/warning
        danger_count = sum(1 for r in latest_readings if r['overall_risk'] == 2)
        warning_count = sum(1 for r in latest_readings if r['overall_risk'] == 1)
        
        cursor.close()
        
        return {
            "total_nodes": total_nodes,
            "active_nodes": active_nodes,
            "nodes_in_danger": danger_count,
            "nodes_in_warning": warning_count,
            "latest_readings": latest_readings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/nodes")
async def get_all_nodes():
    """Get all nodes"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT node_id, location_name, lat, lon, 
                   last_seen, status, installed_at
            FROM nodes
            ORDER BY last_seen DESC
        """)
        nodes = cursor.fetchall()
        cursor.close()
        return {"nodes": nodes}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/nodes/{node_id}/readings")
async def get_node_readings(node_id: str, hours: int = 24):
    """Get readings for specific node"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM sensor_readings
            WHERE node_id = %s 
            AND recorded_at > NOW() - INTERVAL '%s hours'
            ORDER BY timestamp DESC
            LIMIT 1000
        """, (node_id, hours))
        
        readings = cursor.fetchall()
        cursor.close()
        
        return {
            "node_id": node_id,
            "count": len(readings),
            "readings": readings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/alerts")
async def get_alerts(hours: int = 24, limit: int = 50):
    """Get recent alerts"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM alerts
            WHERE created_at > NOW() - INTERVAL '%s hours'
            ORDER BY created_at DESC
            LIMIT %s
        """, (hours, limit))
        
        alerts = cursor.fetchall()
        cursor.close()
        
        return {
            "count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/readings")
async def create_reading(reading: SensorReading):
    """Manually submit sensor reading (HTTP alternative to MQTT)"""
    success = store_sensor_reading(reading)
    
    if success:
        return {"status": "success", "message": "Reading stored"}
    else:
        raise HTTPException(status_code=500, detail="Failed to store reading")

@app.post("/api/alerts")
async def create_alert(alert: AlertData, background_tasks: BackgroundTasks):
    """Manually create alert"""
    alert_id = store_alert(alert)
    
    if alert_id:
        # Send WhatsApp in background
        background_tasks.add_task(send_whatsapp_alert, alert_id, alert)
        return {"status": "success", "alert_id": alert_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to create alert")

# ============= WHATSAPP CHATBOT =============

def get_latest_sensor_data(node_id: str = "SungaiTohor_Node01"):
    """Get latest sensor readings for chatbot responses"""
    conn = get_db_connection()
    if not conn:
        # Fallback to demo data for testing when DB is not available
        from datetime import datetime
        return {
            'node_id': 'SungaiTohor_Node01',
            'timestamp': int(datetime.now().timestamp()),
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
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM sensor_readings 
            WHERE node_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (node_id,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        return data if data else None
    except Exception as e:
        print(f"Error fetching sensor data: {e}")
        # Return demo data instead of None
        return {
            'node_id': 'SungaiTohor_Node01',
            'timestamp': int(datetime.now().timestamp()),
            'water_level': 85.0,
            'tds': 450.0,
            'voc': 350,
            'pm25': 25,
            'pm10': 35,
            'temperature': 28.5,
            'humidity': 75.0,
            'fire_risk': 0,
            'flood_risk': 0,
            'overall_risk': 0
        }

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

def process_chatbot_message(incoming_msg: str, from_number: str):
    """Process incoming WhatsApp message and generate intelligent response"""
    msg_upper = incoming_msg.strip().upper()
    
    # Get latest sensor data
    sensor_data = get_latest_sensor_data()
    
    if not sensor_data:
        return "⚠️ Maaf, sistem sedang offline. Coba lagi nanti.\n\nSorry, system is offline. Try again later."
    
    # Calculate time since last reading
    last_update = datetime.fromtimestamp(sensor_data['timestamp'])
    time_diff = datetime.now() - last_update
    minutes_ago = int(time_diff.total_seconds() / 60)
    
    # STATUS QUERY - Current conditions
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
    elif "TANAM" in msg_upper or "PANEN" in msg_upper or "PERTANIAN" in msg_upper:
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
    
    # EMERGENCY CONTACTS
    elif "BAHAYA" in msg_upper or "DARURAT" in msg_upper or "EMERGENCY" in msg_upper:
        response = """🚨 *KONTAK DARURAT*

🔥 Kebakaran Hutan: 113
🌊 BPBD Riau: (0761) 47777
🚑 Ambulans: 118 / 119
👨‍🚒 Pemadam Desa: [NOMOR LOKAL]
📍 Titik Evakuasi: Balai Desa Sungai Tohor

⚠️ Jika BAHAYA segera hubungi Tim Siaga Desa!

Kirim 'STATUS' untuk kondisi sensor"""
        return response
    
    # FIRE SPECIFIC
    elif "API" in msg_upper or "ASAP" in msg_upper or "SMOKE" in msg_upper or "FIRE" in msg_upper:
        fire_status = ["AMAN ✅", "WASPADA ⚠️", "BAHAYA 🚨"][sensor_data['fire_risk']]
        
        response = f"""🔥 *INFO RISIKO KEBAKARAN*

Status: {fire_status}

🌫️ Gas VOC: {sensor_data['voc']} ppb
💨 Asap PM2.5: {sensor_data['pm25']} µg/m³
🌡️ Suhu: {sensor_data['temperature']:.1f}°C
💧 Kelembaban: {sensor_data['humidity']:.0f}%

"""
        
        if sensor_data['fire_risk'] >= 2:
            response += "⚠️ TINGKAT BAHAYA! Aktifkan Regu Pemadam!\n\n"
        elif sensor_data['fire_risk'] == 1:
            response += "⚠️ Tetap waspada, pantau terus\n\n"
        else:
            response += "✅ Kondisi aman saat ini\n\n"
        
        response += "Kirim 'BAHAYA' untuk kontak darurat"
        return response
    
    # FLOOD SPECIFIC
    elif "BANJIR" in msg_upper or "AIR" in msg_upper or "FLOOD" in msg_upper or "WATER" in msg_upper:
        flood_status = ["AMAN ✅", "WASPADA ⚠️", "BAHAYA 🚨"][sensor_data['flood_risk']]
        
        response = f"""🌊 *INFO RISIKO BANJIR*

Status: {flood_status}

📏 Ketinggian Air: {sensor_data['water_level']:.0f} cm
🧂 Salinitas (TDS): {sensor_data['tds']:.0f} ppm
💧 Kelembaban: {sensor_data['humidity']:.0f}%

"""
        
        if sensor_data['flood_risk'] >= 2:
            response += "⚠️ AIR TINGGI! Siapkan evakuasi!\n\n"
        elif sensor_data['flood_risk'] == 1:
            response += "⚠️ Air naik, tetap waspada\n\n"
        else:
            response += "✅ Ketinggian air normal\n\n"
        
        if sensor_data['tds'] > 1500:
            response += "🧂 PERINGATAN: Air mengandung garam tinggi!\n\n"
        
        response += "Kirim 'TANAM' untuk saran pertanian"
        return response
    
    # DATA HISTORY
    elif "DATA" in msg_upper or "HISTORY" in msg_upper or "RIWAYAT" in msg_upper:
        response = f"""📈 *DATA SENSOR TERKINI*

Node: {sensor_data['node_id']}
Waktu: {last_update.strftime('%d/%m/%Y %H:%M')}

🌊 Air: {sensor_data['water_level']:.0f} cm
🧂 TDS: {sensor_data['tds']:.0f} ppm
🔥 VOC: {sensor_data['voc']} ppb
💨 PM2.5: {sensor_data['pm25']} µg/m³
🌡️ Suhu: {sensor_data['temperature']:.1f}°C
💧 Kelembaban: {sensor_data['humidity']:.0f}%

📊 Dashboard: http://localhost:8501

Kirim 'STATUS' untuk ringkasan"""
        return response
    
    # HELP MENU
    elif "BANTUAN" in msg_upper or "HELP" in msg_upper or "MENU" in msg_upper:
        response = """ℹ️ *MENU PEATGUARD BOT*

📊 Kirim 'STATUS' → Kondisi terkini
🌾 Kirim 'TANAM' → Saran pertanian
🔥 Kirim 'API' → Info risiko kebakaran
🌊 Kirim 'BANJIR' → Info risiko banjir
🚨 Kirim 'BAHAYA' → Kontak darurat
📈 Kirim 'DATA' → Data lengkap sensor

💬 Tanya apa saja tentang kondisi lahan gambut!

🌐 English: Send 'HELP' for menu"""
        return response
    
    # DEFAULT - Friendly response with suggestions
    else:
        response = f"""👋 Terima kasih pesan Anda!

Saya PeatGuard Bot, siap membantu monitoring lahan gambut.

💡 Coba kirim:
• 'STATUS' - Cek kondisi sekarang
• 'TANAM' - Saran pertanian
• 'BANTUAN' - Lihat menu lengkap

📊 Kondisi saat ini:
🌊 Air: {sensor_data['water_level']:.0f}cm
🔥 Risiko: {['Aman','Waspada','Bahaya'][sensor_data['fire_risk']]}

Apa yang ingin Anda tanyakan?"""
        return response

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Webhook endpoint for incoming WhatsApp messages (Twilio)"""
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        incoming_msg = form_data.get('Body', '').strip()
        from_number = form_data.get('From', '')
        to_number = form_data.get('To', '')
        
        print(f"📥 WhatsApp message from {from_number}: {incoming_msg}")
        
        # Process message and get response
        response_text = process_chatbot_message(incoming_msg, from_number)
        
        # Create Twilio response
        resp = MessagingResponse()
        resp.message(response_text)
        
        print(f"📤 Response sent: {response_text[:50]}...")
        
        # Return TwiML response
        return Response(content=str(resp), media_type="application/xml")
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        # Return error message
        resp = MessagingResponse()
        resp.message("Maaf, terjadi error. Coba lagi nanti. / Sorry, error occurred. Try again later.")
        return Response(content=str(resp), media_type="application/xml")

@app.get("/webhook/whatsapp")
async def whatsapp_webhook_get():
    """Handle GET request to webhook (for testing)"""
    return {
        "status": "ok",
        "message": "PeatGuard WhatsApp Bot is active",
        "endpoint": "/webhook/whatsapp",
        "method": "POST",
        "commands": [
            "STATUS - Check current conditions",
            "TANAM - Get farming advice",
            "API - Fire risk info",
            "BANJIR - Flood risk info",
            "BAHAYA - Emergency contacts",
            "BANTUAN - Help menu"
        ]
    }

# ============= RUN SERVER =============

if __name__ == "__main__":
    import uvicorn
    
    print("🌊 Starting PeatSense Backend Server")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
