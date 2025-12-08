import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import io
import base64

st.set_page_config(
    page_title="AirSight Systems | Mission Control",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ultra-Dark Industrial Theme with Glassmorphism
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #161B22 50%, #1A1F29 100%);
        color: #E8E8E8;
    }
    
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1F29 0%, #0E1117 100%);
        border-right: 1px solid #00FF94;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #B8B8B8;
    }
    
    
    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: #00FF94;
        box-shadow: 0 8px 32px 0 rgba(0, 255, 148, 0.2);
    }
    
    
    .kpi-safe {
        background: linear-gradient(135deg, rgba(0, 255, 148, 0.1) 0%, rgba(0, 255, 148, 0.05) 100%);
        border-left: 4px solid #00FF94;
    }
    
    .kpi-warning {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 215, 0, 0.05) 100%);
        border-left: 4px solid #FFD700;
    }
    
    .kpi-hazard {
        background: linear-gradient(135deg, rgba(255, 43, 43, 0.1) 0%, rgba(255, 43, 43, 0.05) 100%);
        border-left: 4px solid #FF2B2B;
    }
    
    
    .main-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #00FF94 0%, #00E5FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #8B8B8B;
        font-size: 0.9rem;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.1); }
    }
    
    .pulse-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #00FF94;
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 8px;
        box-shadow: 0 0 10px #00FF94;
    }
    
    
    .metric-label {
        font-size: 0.75rem;
        color: #8B8B8B;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-unit {
        font-size: 1rem;
        color: #6B6B6B;
        font-weight: 400;
    }
    
    
    .ai-log {
        background: rgba(0, 229, 255, 0.05);
        border: 1px solid #00E5FF;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        line-height: 1.6;
    }
    
    .ai-log-title {
        color: #00E5FF;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    
    button[kind="header"] {
        background-color: rgba(0, 229, 255, 0.1);
        border: 1px solid #00E5FF;
        color: #00E5FF;
    }
    
    button[kind="header"]:hover {
        background-color: rgba(0, 229, 255, 0.2);
        border-color: #00FF94;
        color: #00FF94;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

THRESHOLDS = {
    'dust': {'safe': 500, 'warning': 1000, 'hazard': 1500},      # µg/m³
    'temp': {'safe': 25, 'warning': 30, 'hazard': 35},           # °C
    'tvoc': {'safe': 200, 'warning': 500, 'hazard': 1000},       # ppb
    'eco2': {'safe': 800, 'warning': 1200, 'hazard': 2000}       # ppm
}

def load_sensor_data():
    csv_path = 'data/sensor_log.csv'
    
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return pd.DataFrame()

def get_safety_status(value, metric):

    thresholds = THRESHOLDS.get(metric, {})
    
    if value <= thresholds.get('safe', float('inf')):
        return 'safe', '#00FF94', '✓'
    elif value <= thresholds.get('warning', float('inf')):
        return 'warning', '#FFD700', '⚠️'
    else:
        return 'hazard', '#FF2B2B', '⚠️'

def calculate_aqi(df):
    if df.empty:
        return 0, 'safe'
    
    latest = df.iloc[-1]
    
    # Normalized scoring (0-100 scale)
    scores = []
    
    for metric in ['dust', 'tvoc', 'eco2']:
        value = latest.get(metric, 0)
        max_threshold = THRESHOLDS[metric]['hazard']
        score = min((value / max_threshold) * 100, 100)
        scores.append(score)
    
    aqi = sum(scores) / len(scores)
    
    if aqi < 30:
        return aqi, 'safe'
    elif aqi < 60:
        return aqi, 'warning'
    else:
        return aqi, 'hazard'

def create_pdf_report(df_filtered, time_range_str):

    buffer = io.BytesIO()
    
    # Create PDF with ReportLab
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1A1F29'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Title
    elements.append(Paragraph("AIRSIGHT SYSTEMS", title_style))
    elements.append(Paragraph("Industrial Air Quality Monitoring Report", styles['Heading2']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Report metadata
    metadata = [
        ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['Monitoring Period:', time_range_str],
        ['Total Data Points:', str(len(df_filtered))],
        ['System Status:', 'Operational']
    ]
    
    metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    elements.append(metadata_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Export charts as images
    if not df_filtered.empty:
        # Chart 1: Emissions Trend
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df_filtered['timestamp'],
            y=df_filtered['dust'],
            name='PM2.5 Dust',
            line=dict(color='#FF6B6B', width=2)
        ))
        fig1.add_trace(go.Scatter(
            x=df_filtered['timestamp'],
            y=df_filtered['tvoc'],
            name='TVOC',
            line=dict(color='#4ECDC4', width=2),
            yaxis='y2'
        ))
        fig1.update_layout(
            title='Emissions Trend Over Time',
            xaxis_title='Time',
            yaxis_title='PM2.5 (µg/m³)',
            yaxis2=dict(title='TVOC (ppb)', overlaying='y', side='right'),
            height=300,
            showlegend=True
        )
        
        img1_bytes = fig1.to_image(format="png", width=700, height=300)
        img1 = Image(io.BytesIO(img1_bytes), width=6.5*inch, height=2.5*inch)
        elements.append(img1)
        elements.append(Spacer(1, 0.2*inch))
        
        # Chart 2: Temperature
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_filtered['timestamp'],
            y=df_filtered['temp'],
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.3)',
            line=dict(color='#FF6B6B', width=2),
            name='Temperature'
        ))
        fig2.add_hline(y=30, line_dash="dash", line_color="orange", annotation_text="Warning Threshold")
        fig2.update_layout(
            title='Thermal Conditions',
            xaxis_title='Time',
            yaxis_title='Temperature (°C)',
            height=250,
            showlegend=False
        )
        
        img2_bytes = fig2.to_image(format="png", width=700, height=250)
        img2 = Image(io.BytesIO(img2_bytes), width=6.5*inch, height=2*inch)
        elements.append(img2)
        elements.append(Spacer(1, 0.2*inch))
    
    # Statistical Summary Table
    elements.append(Paragraph("Statistical Summary", heading_style))
    
    if not df_filtered.empty:
        stats_data = [['Parameter', 'Average', 'Maximum', 'Minimum', 'Status']]
        
        params = {
            'PM2.5 Dust (µg/m³)': 'dust',
            'Temperature (°C)': 'temp',
            'TVOC (ppb)': 'tvoc',
            'eCO2 (ppm)': 'eco2'
        }
        
        for param_name, col in params.items():
            if col in df_filtered.columns:
                avg = df_filtered[col].mean()
                max_val = df_filtered[col].max()
                min_val = df_filtered[col].min()
                status, _, _ = get_safety_status(max_val, col)
                status_text = status.upper()
                
                stats_data.append([
                    param_name,
                    f"{avg:.2f}",
                    f"{max_val:.2f}",
                    f"{min_val:.2f}",
                    status_text
                ])
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Add page break before recommendations
    elements.append(PageBreak())
    
    # AI Recommendations
    elements.append(Paragraph("AI-Generated Analysis & Recommendations", heading_style))
    
    comprehensive_report = generate_comprehensive_report(df_filtered, time_range_str)
    
    # Convert report to paragraphs
    for line in comprehensive_report.split('\n'):
        if line.strip():
            if '=' * 10 in line:
                elements.append(Spacer(1, 0.1*inch))
            elif line.strip().startswith(('EXECUTIVE', 'STATISTICAL', 'AI-GENERATED', 'OVERALL', 'GENERAL')):
                elements.append(Spacer(1, 0.15*inch))
                elements.append(Paragraph(f"<b>{line.strip()}</b>", heading_style))
            elif line.strip().startswith(('🔴', '🟡', '🟠', '🟢', '⚠️', '⚡', 'ℹ️', '✅')):
                elements.append(Paragraph(f"<b>{line.strip()}</b>", body_style))
            else:
                elements.append(Paragraph(line.strip(), body_style))
    
    # Build PDF
    pdf.build(elements)
    buffer.seek(0)
    
    return buffer

def generate_comprehensive_report(df_filtered, time_range):

    if df_filtered.empty:
        return "No data available for the selected time range."
    
    report = []
    
    # Executive Summary
    report.append("EXECUTIVE SUMMARY")
    report.append("=" * 80)
    report.append(f"Monitoring Period: {time_range}")
    report.append(f"Total Readings Analyzed: {len(df_filtered)}")
    report.append(f"Data Collection Interval: Continuous (5-second intervals)")
    report.append("")
    
    # Statistical Overview
    report.append("STATISTICAL OVERVIEW")
    report.append("=" * 80)
    
    params = {
        'PM2.5 Dust': ('dust', 'µg/m³', 500, 1000, 1500),
        'Temperature': ('temp', '°C', 25, 30, 35),
        'TVOC': ('tvoc', 'ppb', 200, 500, 1000),
        'eCO2': ('eco2', 'ppm', 800, 1200, 2000)
    }
    
    for param_name, (col, unit, low_thresh, med_thresh, high_thresh) in params.items():
        if col in df_filtered.columns:
            values = df_filtered[col]
            avg = values.mean()
            max_val = values.max()
            min_val = values.min()
            
            # Determine status
            if max_val >= high_thresh:
                status = "CRITICAL"
                emoji = "🔴"
            elif max_val >= med_thresh:
                status = "WARNING"
                emoji = "🟡"
            elif max_val >= low_thresh:
                status = "MODERATE"
                emoji = "🟠"
            else:
                status = "NORMAL"
                emoji = "🟢"
            
            report.append(f"{emoji} {param_name}:")
            report.append(f"   Average: {avg:.2f} {unit}")
            report.append(f"   Maximum: {max_val:.2f} {unit}")
            report.append(f"   Minimum: {min_val:.2f} {unit}")
            report.append(f"   Status: {status}")
            report.append("")
    
    # AI-Generated Recommendations
    report.append("AI-GENERATED RECOMMENDATIONS")
    report.append("=" * 80)
    
    latest = df_filtered.iloc[-1]
    dust_avg = df_filtered['dust'].mean() if 'dust' in df_filtered.columns else 0
    tvoc_avg = df_filtered['tvoc'].mean() if 'tvoc' in df_filtered.columns else 0
    eco2_avg = df_filtered['eco2'].mean() if 'eco2' in df_filtered.columns else 0
    temp_avg = df_filtered['temp'].mean() if 'temp' in df_filtered.columns else 0
    
    # Dust Analysis
    if dust_avg >= 1500:
        report.append("🔴 CRITICAL - PARTICULATE MATTER (PM2.5)")
        report.append("   • IMMEDIATE ACTION: Activate emergency air filtration systems")
        report.append("   • Evacuate non-essential personnel from affected areas")
        report.append("   • Contact environmental compliance officer")
        report.append("   • Investigate source: Check industrial processes, HVAC systems")
        report.append("   • Long-term: Install HEPA filtration units, seal dust sources")
    elif dust_avg >= 1000:
        report.append("🟡 WARNING - PARTICULATE MATTER (PM2.5)")
        report.append("   • Increase ventilation rates by 30-50%")
        report.append("   • Schedule deep cleaning of air ducts")
        report.append("   • Monitor outdoor air quality - may be external source")
        report.append("   • Consider upgrading air filters to MERV 13+")
    elif dust_avg >= 500:
        report.append("🟠 MODERATE - PARTICULATE MATTER (PM2.5)")
        report.append("   • Maintain current filtration protocols")
        report.append("   • Regular filter replacement schedule recommended")
        report.append("   • Monitor trends for any upward patterns")
    else:
        report.append("🟢 NORMAL - PARTICULATE MATTER (PM2.5)")
        report.append("   • Air quality is within safe parameters")
        report.append("   • Continue standard maintenance procedures")
    report.append("")
    
    # Temperature Analysis
    if temp_avg >= 35:
        report.append("🔴 CRITICAL - THERMAL CONDITIONS")
        report.append("   • IMMEDIATE: Reduce heat-generating processes")
        report.append("   • Check HVAC system capacity and functionality")
        report.append("   • Implement worker rotation schedules")
        report.append("   • Provide cooling stations and hydration")
    elif temp_avg >= 30:
        report.append("🟡 WARNING - THERMAL CONDITIONS")
        report.append("   • Optimize HVAC settings for better cooling")
        report.append("   • Ensure adequate air circulation")
        report.append("   • Monitor equipment for heat generation")
    elif temp_avg >= 25:
        report.append("🟠 MODERATE - THERMAL CONDITIONS")
        report.append("   • Temperature approaching upper comfort limits")
        report.append("   • Preventive: Service HVAC before peak periods")
    else:
        report.append("🟢 NORMAL - THERMAL CONDITIONS")
        report.append("   • Temperature within optimal comfort zone")
        report.append("   • Energy efficiency is likely optimal")
    report.append("")
    
    # TVOC Analysis
    if tvoc_avg >= 1000:
        report.append("🔴 CRITICAL - TOTAL VOLATILE ORGANIC COMPOUNDS (TVOC)")
        report.append("   • IMMEDIATE: Identify VOC source (paints, solvents, chemicals)")
        report.append("   • Maximize fresh air intake, open windows if safe")
        report.append("   • Use activated carbon filtration")
        report.append("   • Review chemical storage and handling procedures")
    elif tvoc_avg >= 500:
        report.append("🟡 WARNING - TOTAL VOLATILE ORGANIC COMPOUNDS (TVOC)")
        report.append("   • Increase outdoor air ventilation rates")
        report.append("   • Audit recent activities: painting, cleaning, manufacturing")
        report.append("   • Consider VOC-absorbing materials (plants, air purifiers)")
    elif tvoc_avg >= 200:
        report.append("🟠 MODERATE - TOTAL VOLATILE ORGANIC COMPOUNDS (TVOC)")
        report.append("   • Acceptable levels, but monitor trends")
        report.append("   • Use low-VOC products when possible")
    else:
        report.append("🟢 NORMAL - TOTAL VOLATILE ORGANIC COMPOUNDS (TVOC)")
        report.append("   • VOC levels are minimal and safe")
        report.append("   • Current ventilation strategy is effective")
    report.append("")
    
    # eCO2 Analysis
    if eco2_avg >= 2000:
        report.append("🔴 CRITICAL - EQUIVALENT CO2 (eCO2)")
        report.append("   • IMMEDIATE: Increase outdoor air exchange rate")
        report.append("   • High occupancy detected - reduce density or stagger shifts")
        report.append("   • Check HVAC for recirculation vs. fresh air ratio")
        report.append("   • Symptoms: Drowsiness, headaches may occur")
    elif eco2_avg >= 1200:
        report.append("🟡 WARNING - EQUIVALENT CO2 (eCO2)")
        report.append("   • Moderate ventilation improvement needed")
        report.append("   • Optimize HVAC for better air turnover")
        report.append("   • Consider occupancy-based ventilation controls")
    elif eco2_avg >= 800:
        report.append("🟠 MODERATE - EQUIVALENT CO2 (eCO2)")
        report.append("   • Slightly elevated, typical of occupied spaces")
        report.append("   • Ensure HVAC is functioning per design specifications")
    else:
        report.append("🟢 NORMAL - EQUIVALENT CO2 (eCO2)")
        report.append("   • Excellent ventilation, fresh air circulation optimal")
        report.append("   • Indoor air quality is superior")
    report.append("")
    
    # Overall System Health
    report.append("OVERALL SYSTEM HEALTH ASSESSMENT")
    report.append("=" * 80)
    
    critical_count = 0
    if dust_avg >= 1500: critical_count += 1
    if temp_avg >= 35: critical_count += 1
    if tvoc_avg >= 1000: critical_count += 1
    if eco2_avg >= 2000: critical_count += 1
    
    if critical_count > 0:
        report.append(f"⚠️ SYSTEM STATUS: CRITICAL ({critical_count} parameter(s) in danger zone)")
        report.append("PRIORITY: IMMEDIATE INTERVENTION REQUIRED")
    elif dust_avg >= 1000 or temp_avg >= 30 or tvoc_avg >= 500 or eco2_avg >= 1200:
        report.append("⚡ SYSTEM STATUS: WARNING (Proactive measures recommended)")
        report.append("PRIORITY: SCHEDULE CORRECTIVE ACTIONS WITHIN 24 HOURS")
    elif dust_avg >= 500 or temp_avg >= 25 or tvoc_avg >= 200 or eco2_avg >= 800:
        report.append("ℹ️ SYSTEM STATUS: MODERATE (Monitoring advised)")
        report.append("PRIORITY: ROUTINE MAINTENANCE AND OBSERVATION")
    else:
        report.append("✅ SYSTEM STATUS: OPTIMAL (All parameters within safe limits)")
        report.append("PRIORITY: MAINTAIN CURRENT PROTOCOLS")
    
    report.append("")
    report.append("GENERAL RECOMMENDATIONS FOR AIR QUALITY IMPROVEMENT")
    report.append("=" * 80)
    report.append("1. Regular HVAC Maintenance: Clean filters monthly, service systems quarterly")
    report.append("2. Source Control: Minimize pollutant generation at the source")
    report.append("3. Ventilation Strategy: Ensure adequate fresh air intake (ASHRAE standards)")
    report.append("4. Air Purification: Consider HEPA + activated carbon filtration")
    report.append("5. Monitoring: Continue real-time tracking and trend analysis")
    report.append("6. Occupant Education: Train staff on air quality impact and best practices")
    report.append("7. Green Solutions: Introduce air-purifying plants, eco-friendly materials")
    report.append("8. Building Envelope: Seal leaks, improve insulation to prevent infiltration")
    report.append("")
    report.append("=" * 80)
    report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("AirSight Systems - Industrial Emissions Monitoring Platform")
    report.append("=" * 80)
    
    return "\n".join(report)

def generate_ai_diagnostic(df):

    if df.empty:
        return "⏳ INITIALIZING SENSOR ARRAY... Awaiting telemetry link."
    
    latest = df.iloc[-1]
    alerts = []
    
    # Check each parameter
    dust_status, _, _ = get_safety_status(latest.get('dust', 0), 'dust')
    tvoc_status, _, _ = get_safety_status(latest.get('tvoc', 0), 'tvoc')
    eco2_status, _, _ = get_safety_status(latest.get('eco2', 0), 'eco2')
    temp_status, _, _ = get_safety_status(latest.get('temp', 0), 'temp')
    
    if dust_status == 'hazard':
        alerts.append("⚠️ CRITICAL: Particulate Matter (PM2.5) exceeds regulatory limits")
        alerts.append("→ RECOMMENDED ACTION: Activate emergency filtration systems")
        alerts.append("→ COMPLIANCE: Notify environmental authorities")
    elif dust_status == 'warning':
        alerts.append("⚡ WARNING: Elevated dust levels detected")
        alerts.append("→ RECOMMENDED ACTION: Inspect filtration unit B")
    
    if tvoc_status == 'hazard':
        alerts.append("⚠️ CRITICAL: Total Volatile Organic Compounds at hazardous levels")
        alerts.append("→ RECOMMENDED ACTION: Evacuate Zone 3, engage ventilation protocol")
    elif tvoc_status == 'warning':
        alerts.append("⚡ WARNING: TVOC approaching safety limits")
    
    if eco2_status == 'hazard':
        alerts.append("⚠️ CRITICAL: CO₂ concentration critical")
        alerts.append("→ RECOMMENDED ACTION: Increase air circulation immediately")
    
    if temp_status == 'hazard':
        alerts.append("⚠️ CRITICAL: Thermal conditions exceed operational limits")
    
    if not alerts:
        return "✓ SYSTEM NOMINAL: All parameters within acceptable ranges\n→ Environmental monitoring active\n→ No corrective actions required"
    
    return "\n".join(alerts)


# SIDEBAR


with st.sidebar:
    st.markdown("### 🛰️ AIRSIGHT SYSTEMS")
    st.markdown("---")
    
    # Status Indicator
    st.markdown(
        """
        <div style='display: flex; align-items: center; margin-bottom: 1.5rem;'>
            <span class='pulse-dot'></span>
            <span style='color: #00FF94; font-weight: 600;'>System Online</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Filters
    st.markdown("#### 🏭 Industrial Zone")
    zone = st.selectbox(
        "Select Zone",
        ["Zone A - Manufacturing", "Zone B - Chemical Processing", "Zone C - Warehouse"],
        label_visibility="collapsed"
    )
    
    st.markdown("#### ⏱️ Time Range")
    time_range = st.selectbox(
        "Time Range",
        ["Last 5 Minutes", "Last 15 Minutes", "Last Hour", "Last 6 Hours", "Last 24 Hours"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # PDF Report Generation
    st.markdown("#### 📄 Generate Report")
    
    report_time_range = st.selectbox(
        "Report Period",
        ["Last 30 Minutes", "Last 1 Hour", "Last 6 Hours", "Last 12 Hours", "Last 24 Hours"],
        label_visibility="collapsed"
    )
    
    if st.button("📥 Download PDF Report", use_container_width=True):
        st.session_state['generate_report'] = True
        st.session_state['report_time_range'] = report_time_range
    
    # Auto-refresh toggle
    st.markdown("---")
    auto_refresh = st.checkbox("Auto-Refresh (2s)", value=True)
    
    st.markdown("---")
    st.markdown(
        """
        <div style='font-size: 0.7rem; color: #6B6B6B; margin-top: 2rem;'>
        <b>AIRSIGHT v1.0.0</b><br>
        Industrial IoT Platform<br>
        © 2025 Climate Tech Systems
        </div>
        """,
        unsafe_allow_html=True
    )


# MAIN DASHBOARD


# Header
col_title, col_report = st.columns([4, 1])

with col_title:
    st.markdown("<div class='main-title'>AIRSIGHT</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>REAL-TIME EMISSIONS MONITORING & REGULATORY COMPLIANCE SYSTEM</div>",
        unsafe_allow_html=True
    )

with col_report:
    st.markdown("<br>", unsafe_allow_html=True)
    report_time_range = st.selectbox(
        "📊 Report Period",
        ["Last 30 Minutes", "Last 1 Hour", "Last 6 Hours", "Last 12 Hours", "Last 24 Hours"],
        key="report_dropdown"
    )
    
    if st.button("📥 DOWNLOAD PDF REPORT", use_container_width=True, type="primary"):
        st.session_state['generate_report'] = True
        st.session_state['report_time_range'] = report_time_range

# Create placeholder for auto-refresh
placeholder = st.empty()

# Main rendering loop
with placeholder.container():
    # Load data
    df = load_sensor_data()
    
    if df.empty:
        st.markdown(
            """
            <div class='ai-log' style='text-align: center; padding: 3rem;'>
                <div class='ai-log-title'>⏳ WAITING FOR SENSOR LINK</div>
                <div style='margin-top: 1rem; color: #8B8B8B;'>
                    No telemetry data available. Ensure backend is running and ESP32 is transmitting.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        latest = df.iloc[-1]
        
        
        # TOP KPI ROW (Heads-Up Display)
        
        
        st.markdown("### 📊 LIVE TELEMETRY")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # PM2.5 (Dust)
        dust_val = latest.get('dust', 0)
        dust_status, dust_color, dust_icon = get_safety_status(dust_val, 'dust')
        with col1:
            st.markdown(
                f"""
                <div class='glass-card kpi-{dust_status}'>
                    <div class='metric-label'>{dust_icon} PM2.5 Particulates</div>
                    <div class='metric-value' style='color: {dust_color};'>
                        {dust_val:.2f} <span class='metric-unit'>µg/m³</span>
                    </div>
                </div>

                <div class='glass-card kpi-{temp_status}'>
                    <div class='metric-label'>{temp_icon} Temperature</div>
                    <div class='metric-value' style='color: {temp_color};'>
                        {temp_val:.1f} <span class='metric-unit'>°C</span>
                    </div>
                </div>

                <div class='glass-card kpi-{tvoc_status}'>
                    <div class='metric-label'>{tvoc_icon} TVOC</div>
                    <div class='metric-value' style='color: {tvoc_color};'>
                        {tvoc_val} <span class='metric-unit'>ppb</span>
                    </div>
                </div>

                <div class='glass-card kpi-{eco2_status}'>
                    <div class='metric-label'>{eco2_icon} eCO₂</div>
                    <div class='metric-value' style='color: {eco2_color};'>
                        {eco2_val} <span class='metric-unit'>ppm</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        
        # VISUALIZATION LAYER
        
        
        st.markdown("### 📈 EMISSION TRENDS")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Live Emission Trend (Dust & TVOC)
            fig_emissions = go.Figure()
            
            fig_emissions.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['dust'],
                mode='lines+markers',
                name='PM2.5 Dust',
                line=dict(color='#00FF94', width=2),
                marker=dict(size=6, symbol='circle'),
                hovertemplate='<b>Dust</b>: %{y:.2f} µg/m³<br>%{x}<extra></extra>'
            ))
            
            fig_emissions.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['tvoc'],
                mode='lines+markers',
                name='TVOC',
                line=dict(color='#FFD700', width=2),
                marker=dict(size=6, symbol='diamond'),
                hovertemplate='<b>TVOC</b>: %{y} ppb<br>%{x}<extra></extra>',
                yaxis='y2'
            ))
            
            fig_emissions.update_layout(
                title=dict(
                    text='Live Emission Trend',
                    font=dict(size=16, color='#E8E8E8')
                ),
                template='plotly_dark',
                paper_bgcolor='rgba(22, 27, 34, 0.7)',
                plot_bgcolor='rgba(14, 17, 23, 0.9)',
                hovermode='x unified',
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                xaxis=dict(title='Time', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(title='PM2.5 (µg/m³)', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                yaxis2=dict(
                    title='TVOC (ppb)',
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                height=350
            )
            
            st.plotly_chart(fig_emissions, use_container_width=True)
        
        with chart_col2:
            # Thermal Conditions (Area Chart)
            fig_temp = go.Figure()
            
            fig_temp.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temp'],
                mode='lines',
                name='Temperature',
                line=dict(color='#FF2B2B', width=0),
                fill='tozeroy',
                fillcolor='rgba(255, 43, 43, 0.3)',
                hovertemplate='<b>Temperature</b>: %{y:.1f}°C<br>%{x}<extra></extra>'
            ))
            
            # Add threshold line
            fig_temp.add_hline(
                y=THRESHOLDS['temp']['warning'],
                line_dash='dash',
                line_color='#FFD700',
                annotation_text='Warning Threshold',
                annotation_position='right'
            )
            
            fig_temp.update_layout(
                title=dict(
                    text='Thermal Conditions',
                    font=dict(size=16, color='#E8E8E8')
                ),
                template='plotly_dark',
                paper_bgcolor='rgba(22, 27, 34, 0.7)',
                plot_bgcolor='rgba(14, 17, 23, 0.9)',
                hovermode='x',
                xaxis=dict(title='Time', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(title='Temperature (°C)', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                height=350
            )
            
            st.plotly_chart(fig_temp, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        
        # REGULATORY COMPLIANCE GAUGE
        
        
        st.markdown("### 🎯 REGULATORY COMPLIANCE")
        
        aqi, aqi_status = calculate_aqi(df)
        
        gauge_color = '#00FF94' if aqi_status == 'safe' else ('#FFD700' if aqi_status == 'warning' else '#FF2B2B')
        
        fig_gauge = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=aqi,
            title={'text': 'Air Quality Index (AQI)', 'font': {'size': 20, 'color': '#E8E8E8'}},
            delta={'reference': 30, 'increasing': {'color': '#FF2B2B'}, 'decreasing': {'color': '#00FF94'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': gauge_color},
                'bar': {'color': gauge_color},
                'bgcolor': 'rgba(14, 17, 23, 0.9)',
                'borderwidth': 2,
                'bordercolor': gauge_color,
                'steps': [
                    {'range': [0, 30], 'color': 'rgba(0, 255, 148, 0.2)'},
                    {'range': [30, 60], 'color': 'rgba(255, 215, 0, 0.2)'},
                    {'range': [60, 100], 'color': 'rgba(255, 43, 43, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': '#00E5FF', 'width': 4},
                    'thickness': 0.75,
                    'value': aqi
                }
            }
        ))
        
        fig_gauge.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(22, 27, 34, 0.7)',
            height=300,
            font={'color': '#E8E8E8'}
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        
        # AI DIAGNOSTIC LOG
        
        
        st.markdown("### 🤖 AI SUPERVISOR")
        
        diagnostic = generate_ai_diagnostic(df)
        
        st.markdown(
            f"""
            <div class='ai-log'>
                <div class='ai-log-title'>DIAGNOSTIC LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div style='white-space: pre-line; color: #C8C8C8;'>{diagnostic}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        
        # PDF REPORT GENERATION (Inside container to prevent refresh clearing)
        
        
        if 'generate_report' in st.session_state and st.session_state['generate_report']:
            report_time_range = st.session_state.get('report_time_range', 'Last 1 Hour')
            
            # Parse time range for report
            time_mapping = {
                "Last 30 Minutes": 30,
                "Last 1 Hour": 60,
                "Last 6 Hours": 360,
                "Last 12 Hours": 720,
                "Last 24 Hours": 1440
            }
            
            minutes = time_mapping.get(report_time_range, 60)
            cutoff = datetime.now() - timedelta(minutes=minutes)
            
            # Filter data for report
            df_report = df[df['timestamp'] >= cutoff].copy()
            
            if not df_report.empty:
                try:
                    with st.spinner('🔄 Generating comprehensive PDF report with AI analysis...'):
                        pdf_buffer = create_pdf_report(df_report, report_time_range)
                    
                    # Create download button
                    filename = f"AirSight_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    
                    st.success("✅ Report generated successfully!")
                    st.download_button(
                        label="📥 Click Here to Download Your PDF Report",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    # Don't reset flag yet - keep button visible
                    if st.button("🔄 Generate New Report", use_container_width=True):
                        st.session_state['generate_report'] = False
                        st.rerun()
                    
                    # Pause auto-refresh while showing download
                    auto_refresh = False
                    
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.session_state['generate_report'] = False
            else:
                st.warning(f"⚠️ No data available for {report_time_range}. Please select a different time range.")
                st.session_state['generate_report'] = False

# Auto-refresh logic
if auto_refresh:
    time.sleep(2)
    st.rerun()
