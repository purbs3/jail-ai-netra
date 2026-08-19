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
import sys
import warnings
warnings.filterwarnings('ignore')

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

st.set_page_config(page_title="NETRA - BPR&D", layout="wide", initial_sidebar_state="expanded")

# ==============================================================
#  CSS: हैमबर्गर विजिबल + मोबाइल रेस्पॉन्सिव (बिल्कुल सटीक)
# ==============================================================
css_code = """
<style>
    /* Default Streamlit elements hide karo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] { display: none !important; }
    .stAppDeployButton { display: none !important; }

    /* ----- HEADER (पूरी तरह visible) ----- */
    header {
        visibility: visible !important;
        display: block !important;
        height: 60px !important;
        background: transparent !important;
    }

    /* ----- साइडबार हैमबर्गर (Open/Close बटन) - हमेशा दिखेगा ----- */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background-color: #0B4F6C !important;
        color: white !important;
        border-radius: 50% !important;
        width: 46px !important;
        height: 46px !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 8px 12px !important;
        border: 3px solid #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        z-index: 999999 !important;
        transition: 0.2s !important;
        cursor: pointer !important;
    }
    [data-testid="collapsedControl"]:hover {
        transform: scale(1.08) !important;
        background-color: #1a6a8a !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: white !important;
        width: 28px !important;
        height: 28px !important;
        stroke: white !important;
        stroke-width: 2px !important;
    }

    /* ----- हेडर (सरकारी लुक) ----- */
    .gov-header {
        background: white;
        padding: 0.5rem 1.2rem;
        border-bottom: 4px solid #0B4F6C;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .gov-title {
        font-weight: 700;
        font-size: 1.2rem;
        color: #1a1a1a;
        margin: 0;
    }
    .gov-title span { color: #0B4F6C; }
    .gov-badge {
        background: #0B4F6C;
        color: white;
        padding: 2px 14px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .tricolor-line {
        height: 4px;
        background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 33%, #138808 66%);
        margin-top: 6px;
        border-radius: 2px;
    }

    /* ----- साइडबार मेन्यू (Selectbox) ----- */
    .stSelectbox label { display: none !important; }
    .stSelectbox > div > div {
        border: 2px solid #0B4F6C !important;
        border-radius: 8px !important;
        background-color: white !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
        transition: 0.2s !important;
    }
    .stSelectbox > div > div > div {
        font-weight: 600 !important;
        color: #0B4F6C !important;
        font-size: 14px !important;
        padding: 4px 10px !important;
    }

    /* ----- मेट्रिक कार्ड्स ----- */
    .metric-card {
        background: white;
        padding: 14px 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-left: 5px solid #0B4F6C;
        margin: 4px 0;
        height: 100%;
        transition: 0.2s;
    }
    .metric-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0B4F6C;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.7rem;
        color: #6b7a8a;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }

    .risk-badge { padding: 3px 16px; border-radius: 30px; font-weight: 700; font-size: 0.85rem; }
    .risk-high { background: #fee2e2; color: #dc2626; }
    .risk-mid { background: #fef9c3; color: #ca8a04; }
    .risk-low { background: #dcfce7; color: #16a34a; }

    .footer-text {
        font-size: 0.7rem;
        color: #8a9aa8;
        text-align: center;
        border-top: 1px solid #e6e9ef;
        padding-top: 12px;
        margin-top: 20px;
    }

    /* ========================================================= */
    /*  मोबाइल रेस्पॉन्सिव (स्क्रीन < 768px) - बहुत जरूरी       */
    /* ========================================================= */
    @media (max-width: 768px) {
        /* हैमबर्गर को मोबाइल पर और बड़ा और टच-फ्रेंडली */
        [data-testid="collapsedControl"] {
            width: 52px !important;
            height: 52px !important;
            margin: 6px 10px !important;
        }
        [data-testid="collapsedControl"] svg {
            width: 32px !important;
            height: 32px !important;
        }

        /* हेडर का टेक्स्ट छोटा */
        .gov-title { font-size: 0.95rem !important; }
        .gov-badge { font-size: 0.55rem !important; padding: 2px 10px; }

        /* मेट्रिक कार्ड्स - फॉन्ट छोटा और पैडिंग कम */
        .metric-card { padding: 10px 12px; }
        .metric-value { font-size: 1.4rem !important; }
        .metric-label { font-size: 0.6rem !important; }
        
        /* साइडबार का मेन्यू फॉन्ट */
        .stSelectbox > div > div > div { font-size: 13px !important; }
    }

    /* बहुत छोटी स्क्रीन ( < 480px ) */
    @media (max-width: 480px) {
        .gov-title { font-size: 0.8rem !important; }
        .metric-value { font-size: 1.2rem !important; }
        [data-testid="collapsedControl"] { width: 48px !important; height: 48px !important; }
    }
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("""
<div class="gov-header">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <div>
            <div style="display:flex; align-items:baseline; gap:8px; flex-wrap:wrap;">
                <div class="gov-title">Bharat Sarkar <span>| NETRA</span></div>
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

# ==========================================================
# 1. DATABASE (SQLite)
# ==========================================================
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

# ==========================================================
# 2. LOGIN SYSTEM
# ==========================================================
def check_password(username, password):
    users = {"admin": "admin123", "jailer": "jailer123", "dgp": "dgp123"}
    return username in users and users[username] == password

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center; color:#0B4F6C;'>[+] NETRA - Government Login Portal</h2>", unsafe_allow_html=True)
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
                    st.error("Invalid credentials.")
    st.stop()

def has_access(required_role):
    if st.session_state.role == "admin": return True
    if required_role == "jailer" and st.session_state.role in ["jailer", "admin"]: return True
    if required_role == "dgp" and st.session_state.role in ["dgp", "admin"]: return True
    return False

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown(f"<div style='font-size:13px; color:#0B4F6C; font-weight:bold;'>User: {st.session_state.username.upper()} [{st.session_state.role}]</div>", unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:5px 0 10px 0;">
        <div style="font-size:22px; font-weight:800; color:#0B4F6C;">NETRA</div>
        <div style="font-size:11px; color:#8a9aa8;">Secure Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Navigation")
    page = st.selectbox("Menu", ["Dashboard", "Visitor Intelligence", "Biometric Scan", "Network Analysis", "Generate Reports"], label_visibility="collapsed")
    st.markdown('<hr>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-size:11px; font-weight:700; color:#8a9aa8;">SYSTEM HEALTH</div>
    <div style="background:#f8fafc; padding:8px 10px; border-radius:8px; font-size:12px; margin-top:5px;">
        <div>[+] CPU: 34%</div>
        <div>[~] Memory: 72%</div>
        <div>[+] AI Engine: Active (Mock)</div>
        <div>[+] DB: SQLite Connected</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    
    # Logout Button inside sidebar
    if st.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    uploaded_file = st.file_uploader("Import Logs (CSV)", type=['csv'], label_visibility="collapsed")

# ---- DATA LOADING ----
df_db = load_visits()
if uploaded_file is not None:
    df_csv = pd.read_csv(uploaded_file)
    df_csv.columns = [c.lower() for c in df_csv.columns]
    for _, row in df_csv.iterrows():
        save_visit(row.get('visitor_name', 'Unknown'), row.get('inmate_id', 'N/A'), 
                   row.get('duration', 0), row.get('risk_score', 0), 0, "")
    st.success(f"[+] {len(df_csv)} records imported!")

df = df_db.copy()
if df.empty:
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

# ---- AI LOGIC ----
visitor_counts = df['visitor_name'].value_counts()
frequent_visitors = visitor_counts[visitor_counts >= 3].index.tolist()
df['Date'] = pd.to_datetime(df['visit_date'])
daily_multi = df.groupby(['visitor_name', 'Date'])['inmate_id'].nunique()
suspicious_daily = daily_multi[daily_multi >= 2].index.get_level_values(0).unique().tolist()
suspects = list(set(frequent_visitors + suspicious_daily))

if len(suspects) >= 3:
    risk_level, risk_class = "HIGH", "risk-high"
elif len(suspects) >= 1:
    risk_level, risk_class = "MEDIUM", "risk-mid"
else:
    risk_level, risk_class = "LOW", "risk-low"

# ==========================================================
# EMAIL & PDF FUNCTIONS
# ==========================================================
def send_email_alert(visitor_name, risk_score, inmate_id):
    try:
        sender = st.secrets.get("EMAIL_SENDER", "your-email@gmail.com")
        password = st.secrets.get("EMAIL_PASSWORD", "your-password")
        receiver = st.secrets.get("EMAIL_RECEIVER", "superintendent@jail.gov.in")
        subject = "HIGH RISK ALERT - NETRA System"
        body = f"ALERT: High risk visitor detected.\nName: {visitor_name}\nRisk Score: {risk_score}%\nLinked Inmate: {inmate_id}\nTime: {datetime.datetime.now()}"
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = sender, receiver, subject
        msg.attach(MIMEText(body, 'plain'))
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        return True
    except Exception as e:
        st.warning(f"Email alert failed: {e}")
        return False

def generate_pdf_report(data):
    if not PDF_AVAILABLE:
        st.error("PDF library not installed.")
        return None
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

def face_match(captured_img):
    return random.choice([(False, None), (True, "mock_blacklist.jpg")])

# ==========================================================
# PAGE RENDER
# ==========================================================
if page == "Dashboard":
    st.markdown("<h2 style='font-weight:600;'>Executive Dashboard</h2>", unsafe_allow_html=True)
    # MOBILE RESPONSIVE: 4 metrics in 2 columns (2+2) so they don't squish on mobile
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{df['visitor_name'].nunique()}</div><div class="metric-label">Total Visitors</div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="metric-card" style="border-left-color: {'#dc2626' if risk_level=='HIGH' else '#ca8a04' if risk_level=='MEDIUM' else '#16a34a'};"><div class="metric-value"><span class="risk-badge {risk_class}">{risk_level}</span></div><div class="metric-label">Security Alert</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{df['inmate_id'].nunique()}</div><div class="metric-label">Total Inmates</div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total Records</div></div>""", unsafe_allow_html=True)
    
    st.subheader("Last 20 Activity Logs")
    st.dataframe(df.head(20), use_container_width=True)

elif page == "Visitor Intelligence":
    st.markdown("<h2 style='font-weight:600;'>Visitor Intelligence Unit</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["All History", "Flagged Suspects"])
    with tab1: st.dataframe(df, use_container_width=True)
    with tab2:
        if suspects:
            st.warning(f"ALERT: {len(suspects)} suspects flagged.")
            for name in suspects:
                st.markdown(f"**{name}** - Visits: {visitor_counts.get(name,0)}")
                st.progress(min(1.0, visitor_counts.get(name,0)/5))
        else: st.success("All clear.")

elif page == "Biometric Scan":
    st.markdown("<h2 style='font-weight:600;'>AI Face Detection (Mock Mode)</h2>", unsafe_allow_html=True)
    st.caption("Captures face and simulates Blacklist matching.")
    col_cam, col_info = st.columns([2,1])
    with col_cam:
        img_file = st.camera_input("Capture Face")
        if img_file is not None:
            img = Image.open(io.BytesIO(img_file.getvalue())).convert("RGB")
            draw = ImageDraw.Draw(img)
            w, h = img.size
            draw.rectangle([int(w*0.25), int(h*0.25), int(w*0.75), int(h*0.75)], outline="#00FF00", width=4)
            draw.text((int(w*0.25), int(h*0.25)-20), "SCANNING...", fill="#00FF00")
            st.image(img, caption="Processed Feed", use_container_width=True)
            with st.spinner("Matching..."):
                is_match, path = face_match(img)
            risk = random.randint(10,95)
            if is_match or risk > 75:
                st.error(f"HIGH RISK! Score: {risk}%")
                if st.button("Send Email Alert"):
                    send_email_alert("Unknown", risk, "I-101")
                    st.success("Alert sent!")
            else:
                st.success(f"Low Risk. Score: {risk}%")
            save_visit("Camera_Scan", "I-999", 0, risk, 1 if is_match else 0, "")
    with col_info:
        st.markdown("#### Profile")
        st.text_input("Name")
        st.text_input("Aadhar")
        if st.button("Manual Check-in"):
            save_visit("Manual", "I-001", 30, 20, 0, "")
            st.success("Logged!")

elif page == "Network Analysis":
    st.markdown("<h2 style='font-weight:600;'>Intelligence Network Map</h2>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12,6))
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['visitor_name'], row['inmate_id'])
    color_map = ['#dc2626' if node in suspects else ('#0B4F6C' if node.startswith('I-') else '#FF9933') for node in G.nodes()]
    nx.draw(G, with_labels=True, node_color=color_map, node_size=1500, font_size=9, pos=nx.spring_layout(G, seed=42))
    st.pyplot(fig)

elif page == "Generate Reports":
    st.markdown("<h2 style='font-weight:600;'>Generate Official Reports</h2>", unsafe_allow_html=True)
    if has_access("jailer"):
        if st.button("Download Monthly Report (PDF)"):
            if PDF_AVAILABLE:
                pdf_path = generate_pdf_report(df.head(100))
                if pdf_path:
                    with open(pdf_path, "rb") as f:
                        st.download_button("Download", f, file_name="NETRA_Report.pdf")
            else:
                st.error("PDF module missing.")
        st.download_button("Download Raw CSV", df.to_csv(index=False).encode('utf-8'), file_name="NETRA_Data.csv")
    else:
        st.warning("Restricted to Jailer/Admin.")

st.markdown("""
<div class="footer-text">
    (C) 2026 BPR&D, MHA | NETRA v3.0 | Persistent DB + Mock AI
</div>
""", unsafe_allow_html=True)
