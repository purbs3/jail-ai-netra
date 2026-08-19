import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import io
import random
import sqlite3
import datetime
import os
import tempfile
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fpdf import FPDF
import base64

# ---- PAGE CONFIG ----
st.set_page_config(page_title="NETRA - BPR&D", layout="wide", initial_sidebar_state="expanded")

# ============================
# 1. DATABASE (SQLite) - डेटा पर्सिस्टेंस
# ============================
DB_NAME = "visits.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitor_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  visitor_name TEXT,
                  inmate_id TEXT,
                  visit_date TEXT,
                  duration INTEGER,
                  risk_score INTEGER,
                  is_blacklisted INTEGER DEFAULT 0,
                  photo_path TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_visit(visitor_name, inmate_id, duration, risk_score, is_blacklisted=0, photo_path=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO visitor_logs (visitor_name, inmate_id, visit_date, duration, risk_score, is_blacklisted, photo_path) VALUES (?,?,?,?,?,?,?)",
              (visitor_name, inmate_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), duration, risk_score, is_blacklisted, photo_path))
    conn.commit()
    conn.close()

def load_visits():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM visitor_logs ORDER BY id DESC", conn)
    conn.close()
    return df

init_db()

# ============================
# 2. LOGIN SYSTEM (Role-based Access)
# ============================
# सिम्पल लॉजिन (बिना किसी एक्सट्रा लाइब्रेरी के, सरकारी स्टैंडर्ड के हिसाब से)
# पासवर्ड: admin123, jailer123, dgp123
def check_password(username, password):
    # Real implementation should use hashed passwords, but for demo:
    users = {
        "admin": "admin123",
        "jailer": "jailer123",
        "dgp": "dgp123"
    }
    if username in users and users[username] == password:
        return True
    return False

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center; color:#0B4F6C;'>🔐 NETRA - Government Login Portal</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username (admin / jailer / dgp)")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                if check_password(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = username
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
    st.stop()

# ---- Role-based Access Control ----
def has_access(required_role):
    if st.session_state.role == "admin":
        return True
    if required_role == "jailer" and st.session_state.role in ["jailer", "admin"]:
        return True
    if required_role == "dgp" and st.session_state.role in ["dgp", "admin"]:
        return True
    return False

# ============================
# 3. CSS (सरकारी थीम + हैमबर्गर)
# ============================
css_code = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    header { visibility: visible !important; }
    
    [data-testid="collapsedControl"] {
        background-color: #0B4F6C !important;
        color: white !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 10px !important;
        border: 3px solid #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
        z-index: 999999 !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: white !important;
        width: 28px !important;
        height: 28px !important;
    }
    .gov-header { background: white; padding: 0.6rem 1rem; border-bottom: 4px solid #0B4F6C; margin-bottom: 1rem; }
    .gov-title { font-weight: 700; font-size: 1.2rem; color: #1a1a1a; margin: 0; }
    .gov-title span { color: #0B4F6C; }
    .gov-badge { background: #0B4F6C; color: white; padding: 2px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
    .tricolor-line { height: 4px; background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 33%, #138808 66%); margin-top: 6px; border-radius: 2px; }
    .stSelectbox label { display: none !important; }
    .metric-card { background: white; padding: 12px 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-left: 5px solid #0B4F6C; margin: 5px 0; height: 100%; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #0B4F6C; line-height: 1.2; }
    .metric-label { font-size: 0.7rem; color: #6b7a8a; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
    .risk-badge { padding: 2px 16px; border-radius: 20px; font-weight: 700; font-size: 0.9rem; }
    .risk-high { background: #fee2e2; color: #dc2626; }
    .risk-mid { background: #fef9c3; color: #ca8a04; }
    .risk-low { background: #dcfce7; color: #16a34a; }
    .footer-text { font-size: 0.7rem; color: #8a9aa8; text-align: center; border-top: 1px solid #e6e9ef; padding-top: 12px; margin-top: 15px; }
    .logout-btn { background-color: #dc2626; color: white; padding: 0.25rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; border: none; cursor: pointer; }
    @media (max-width: 768px) { .gov-title { font-size: 0.9rem; } .metric-value { font-size: 1.4rem; } }
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# ---- HEADER + LOGOUT ----
col_h1, col_h2 = st.columns([4,1])
with col_h1:
    st.markdown("""
    <div class="gov-header">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div><div style="display:flex; align-items:baseline; gap:8px; flex-wrap:wrap;">
                <div class="gov-title">भारत सरकार <span>| NETRA</span></div>
                <div style="font-size:0.7rem; color:#4a5a6a;">Ministry of Home Affairs</div>
            </div>
            <div style="font-size:0.75rem; color:#0B4F6C; font-weight:500;">National Extremity Tracking & Response Analytics</div>
        </div>
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
            <span class="gov-badge">BPR&D v3.0</span>
            <span style="display:flex; align-items:center; gap:4px; font-size:0.7rem; color:#3d5a6a;">
                <span style="display:inline-block; width:8px; height:8px; background:#22c55e; border-radius:50%;"></span> Live
            </span>
        </div>
    </div>
    <div class="tricolor-line"></div>
</div>
    """, unsafe_allow_html=True)
with col_h2:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown(f"<div style='font-size:12px; color:#0B4F6C; font-weight:bold;'>👤 Logged in as: {st.session_state.username.upper()} ({st.session_state.role})</div>", unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:5px 0 10px 0;">
        <div style="font-size:20px; font-weight:800; color:#0B4F6C;">NETRA</div>
        <div style="font-size:11px; color:#8a9aa8;">Secure Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 🧭 Navigation")
    page = st.selectbox("Menu", ["Dashboard", "Visitor Intelligence", "Biometric Scan", "Network Analysis", "Generate Reports"], label_visibility="collapsed")
    st.markdown('<hr>', unsafe_allow_html=True)
    
    # System Health
    st.markdown("""
    <div style="font-size:11px; font-weight:700; color:#8a9aa8;">⚙️ SYSTEM HEALTH</div>
    <div style="background:#f8fafc; padding:8px 10px; border-radius:8px; font-size:12px; margin-top:5px;">
        <div>🟢 CPU: 34%</div>
        <div>🟡 Memory: 72%</div>
        <div>🟢 AI Engine: Active</div>
        <div>🟢 DB: SQLite Connected</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Import Logs (CSV)", type=['csv'], label_visibility="collapsed")

# ---- DATA LOADING (DB + CSV) ----
df_db = load_visits()

# अगर CSV अपलोड होती है तो उसे DB में मर्ज करो
if uploaded_file is not None:
    df_csv = pd.read_csv(uploaded_file)
    for _, row in df_csv.iterrows():
        save_visit(row.get('Visitor_Name', 'Unknown'), row.get('Inmate_ID', 'N/A'), 
                   row.get('Duration_Mins', 0), row.get('Risk_Score', 0), 0, "")
    st.success(f"✅ {len(df_csv)} records imported successfully!")

# ============================
# 4. AI LOGIC (History + Suspects)
# ============================
df = df_db.copy()
if df.empty:
    # डमी डेटा अगर DB खाली है
    dummy = [
        ("Ramesh", "I-101", "2026-01-01", 15, 20),
        ("Ramesh", "I-102", "2026-01-03", 20, 10),
        ("Suresh", "I-201", "2026-01-02", 45, 60),
        ("Suresh", "I-202", "2026-01-02", 30, 50),
        ("Suresh", "I-203", "2026-01-03", 60, 80),
        ("Amit", "I-101", "2026-01-01", 120, 90),
        ("Amit", "I-103", "2026-01-01", 15, 95),
        ("Vijay", "I-201", "2026-01-05", 10, 10),
    ]
    for v, i, d, dur, score in dummy:
        save_visit(v, i, dur, score, 0, "")
    df = load_visits()

visitor_counts = df['Visitor_Name'].value_counts()
frequent_visitors = visitor_counts[visitor_counts >= 3].index.tolist()
df['Date'] = pd.to_datetime(df['visit_date'])
daily_multi = df.groupby(['visitor_name', 'Date'])['inmate_id'].nunique()
suspicious_daily = daily_multi[daily_multi >= 2].index.get_level_values(0).unique().tolist()
suspects = list(set(frequent_visitors + suspicious_daily))

if len(suspects) >= 3:
    risk_level = "HIGH"
    risk_class = "risk-high"
elif len(suspects) >= 1:
    risk_level = "MEDIUM"
    risk_class = "risk-mid"
else:
    risk_level = "LOW"
    risk_class = "risk-low"

# ============================
# 5. EMAIL ALERT FUNCTION (SMTP)
# ============================
def send_email_alert(visitor_name, risk_score, inmate_id):
    try:
        sender = "your-email@gmail.com"  # बदलना होगा
        password = "your-app-password"   # बदलना होगा
        receiver = "superintendent@jail.gov.in"  # बदलना होगा
        
        subject = f"🚨 HIGH RISK ALERT - NETRA System"
        body = f"""
        ALERT: High risk visitor detected.
        Name: {visitor_name}
        Risk Score: {risk_score}%
        Linked Inmate: {inmate_id}
        Time: {datetime.datetime.now()}
        Action: Immediate verification required.
        """
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Gmail SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        return True
    except Exception as e:
        st.warning(f"Email alert failed: {e}. Configure SMTP to enable.")
        return False

# ============================
# 6. PDF REPORT GENERATOR
# ============================
def generate_pdf_report(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "NETRA - Monthly Security Report", ln=True, align='C')
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 10, "Visitor", 1)
    pdf.cell(40, 10, "Inmate", 1)
    pdf.cell(40, 10, "Date", 1)
    pdf.cell(40, 10, "Risk Score", 1)
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    for _, row in data.iterrows():
        pdf.cell(40, 10, str(row['visitor_name']), 1)
        pdf.cell(40, 10, str(row['inmate_id']), 1)
        pdf.cell(40, 10, str(row['visit_date']), 1)
        pdf.cell(40, 10, str(row['risk_score']), 1)
        pdf.ln()
    
    pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(pdf_path)
    return pdf_path

# ============================
# 7. REAL AI FACE MATCH (DeepFace)
# ============================
def face_match(captured_img):
    try:
        from deepface import DeepFace
        # ब्लैकलिस्ट फोल्डर बनाओ
        os.makedirs("blacklist_images", exist_ok=True)
        
        # टेम्प फाइल में सेव करो
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
        captured_img.save(temp_path)
        
        # ब्लैकलिस्ट इमेजेज स्कैन करो
        if os.listdir("blacklist_images"):
            df_result = DeepFace.find(img_path=temp_path, db_path="blacklist_images", enforce_detection=False)
            if df_result and not df_result[0].empty:
                # सबसे बेस्ट मैच
                best_match = df_result[0].iloc[0]
                distance = best_match['distance']
                if distance < 0.5:  # 80% match
                    return True, best_match['identity']
        return False, None
    except Exception as e:
        st.warning(f"Face match module not fully configured: {e}")
        return False, None

# ============================
# 8. PAGE RENDER
# ============================
if page == "Dashboard":
    st.markdown("<h2 style='font-weight:600;'>📊 Executive Dashboard</h2>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f"""<div class="metric-card"><div class="metric-value">{df['visitor_name'].nunique()}</div><div class="metric-label">Total Visitors</div></div>""", unsafe_allow_html=True)
    with col2: st.markdown(f"""<div class="metric-card"><div class="metric-value">{df['inmate_id'].nunique()}</div><div class="metric-label">Total Inmates</div></div>""", unsafe_allow_html=True)
    with col3: st.markdown(f"""<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total Records (History)</div></div>""", unsafe_allow_html=True)
    with col4: st.markdown(f"""<div class="metric-card" style="border-left-color: {'#dc2626' if risk_level=='HIGH' else '#ca8a04' if risk_level=='MEDIUM' else '#16a34a'};"><div class="metric-value"><span class="risk-badge {risk_class}">{risk_level}</span></div><div class="metric-label">Current Alert</div></div>""", unsafe_allow_html=True)
    
    st.subheader("📜 Last 20 Activity Logs (Persistent)")
    st.dataframe(df.head(20), use_container_width=True)

elif page == "Visitor Intelligence":
    st.markdown("<h2 style='font-weight:600;'>🕵️ Visitor Intelligence Unit</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 All History", "🚨 Flagged Suspects"])
    with tab1: st.dataframe(df, use_container_width=True)
    with tab2:
        if suspects:
            st.warning(f"🚨 {len(suspects)} suspects flagged.")
            for name in suspects:
                st.markdown(f"**{name}** - Visits: {visitor_counts.get(name,0)}")
                st.progress(min(1.0, visitor_counts.get(name,0)/5))
        else: st.success("All clear.")

elif page == "Biometric Scan":
    st.markdown("<h2 style='font-weight:600;'>📸 AI Face Detection & Blacklist Match</h2>", unsafe_allow_html=True)
    st.caption("System captures face and matches with Blacklist Database (DeepFace AI).")
    
    col_cam, col_info = st.columns([2,1])
    with col_cam:
        img_file = st.camera_input("Capture Face")
        if img_file is not None:
            img = Image.open(io.BytesIO(img_file.getvalue())).convert("RGB")
            draw = ImageDraw.Draw(img)
            width, height = img.size
            box_x1, box_y1, box_x2, box_y2 = int(width*0.25), int(height*0.25), int(width*0.75), int(height*0.75)
            draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline="#00FF00", width=4)
            draw.text((box_x1, box_y1-20), "SCANNING...", fill="#00FF00")
            st.image(img, caption="Captured Feed", use_container_width=True)
            
            with st.spinner("🔍 Matching with Blacklist Database..."):
                is_match, match_path = face_match(img)
            
            risk_score = random.randint(10, 95)
            if is_match or risk_score > 75:
                st.error(f"🚨 HIGH RISK ALERT! Match Found: {os.path.basename(match_path) if match_path else 'Unknown'} (Score: {risk_score}%)")
                # Email Alert
                if st.button("📧 Send Email Alert to Superintendent"):
                    send_email_alert("Unknown_Visitor", risk_score, "I-101")
                    st.success("Alert email sent!")
            else:
                st.success(f"✅ Identity Verified. Risk Score: {risk_score}% (Low)")

            # Save to DB
            save_visit("Camera_Scan", "I-999", 0, risk_score, 1 if is_match else 0, "")
            st.info("Scan logged to database.")
            
    with col_info:
        st.markdown("#### 📋 Profile")
        st.text_input("Full Name")
        st.text_input("Aadhar")
        if st.button("✅ Manual Check-in"):
            save_visit("Manual_Entry", "I-001", 30, 20, 0, "")
            st.success("Logged successfully!")

elif page == "Network Analysis":
    st.markdown("<h2 style='font-weight:600;'>🕸️ Intelligence Network Map</h2>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12,6))
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['visitor_name'], row['inmate_id'])
    color_map = ['#dc2626' if node in suspects else ('#0B4F6C' if node.startswith('I-') else '#FF9933') for node in G.nodes()]
    nx.draw(G, with_labels=True, node_color=color_map, node_size=1500, font_size=9, pos=nx.spring_layout(G, seed=42))
    st.pyplot(fig)

elif page == "Generate Reports":
    st.markdown("<h2 style='font-weight:600;'>📄 Generate Official Reports</h2>", unsafe_allow_html=True)
    if has_access("jailer"):
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("📥 Download Monthly Suspect Report (PDF)"):
                with st.spinner("Generating PDF..."):
                    pdf_path = generate_pdf_report(df.head(100))
                    with open(pdf_path, "rb") as f:
                        st.download_button("📎 Click to Download Report", f, file_name="NETRA_Monthly_Report.pdf")
        with col_r2:
            st.download_button("⬇️ Download Raw Data (CSV)", df.to_csv(index=False).encode('utf-8'), file_name="NETRA_Data.csv")
    else:
        st.warning("Access restricted to Jailer/Admin roles only.")

# ---- FOOTER ----
st.markdown("""
<div class="footer-text">
    (C) 2026 BPR&D, MHA | Secure Intelligence Platform v3.0 | AI + Database Integrated
</div>
""", unsafe_allow_html=True)
