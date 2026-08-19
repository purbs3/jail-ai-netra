import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image
import io

# ---- PAGE CONFIG ----
st.set_page_config(page_title="NETRA - BPR&D | MHA", page_icon="⚖️", layout="wide")

# ---- CUSTOM CSS FOR GOVERNMENT THEME ----
st.markdown("""
<style>
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Government Tricolor Header */
    .gov-header {
        background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
        padding: 0.5rem;
        border-radius: 0 0 10px 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .gov-title {
        font-family: 'Arial', sans-serif;
        font-weight: 900;
        color: #0B4F6C;
        text-align: center;
        margin: 0;
    }
    .gov-subtitle {
        text-align: center;
        color: #1a1a1a;
        font-size: 0.9rem;
        font-weight: 600;
        background: rgba(255,255,255,0.8);
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
        margin: 0 auto;
    }
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 6px solid #0B4F6C;
        margin: 5px 0;
        transition: 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    .metric-label {
        font-size: 0.8rem;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0B4F6C;
    }
    /* Risk Badge */
    .risk-high { background-color: #dc3545; color: white; padding: 2px 12px; border-radius: 20px; font-size:0.8rem;}
    .risk-mid { background-color: #ffc107; color: black; padding: 2px 12px; border-radius: 20px; font-size:0.8rem;}
    .risk-low { background-color: #28a745; color: white; padding: 2px 12px; border-radius: 20px; font-size:0.8rem;}
    /* Responsive tweaks */
    @media (max-width: 768px) {
        .metric-value { font-size: 1.5rem; }
        .gov-title { font-size: 1.2rem; }
    }
</style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("""
<div class="gov-header">
    <div style="display: flex; justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap;">
        <span style="font-size: 2rem;">🕉️</span>
        <div>
            <h1 class="gov-title">भारत सरकार | GOVERNMENT OF INDIA</h1>
            <p style="text-align: center; margin:0; font-weight:bold; color:#0B4F6C;">
                Ministry of Home Affairs | Bureau of Police Research & Development (BPR&D)
            </p>
        </div>
        <span style="font-size: 2rem;">⚖️</span>
    </div>
    <div style="text-align: center;">
        <span class="gov-subtitle">🔍 NETRA - National Extremity Tracking & Response Analytics</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- SIDEBAR ----
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/justice.png", width=80)
    st.markdown("### 🛡️ Command Center")
    uploaded_file = st.file_uploader("📂 Upload Visitor Log (CSV)", type=['csv'])
    
    st.markdown("---")
    st.markdown("**⚙️ System Status**")
    st.success("🟢 All Systems Operational")
    st.caption("v2.0 - AI Surveillance Active")
    
    if uploaded_file:
        st.success("File Loaded Successfully")
    else:
        st.info("ℹ️ Using Default Demo Data")

# ---- DATA LOADER ----
@st.cache_data
def load_data(file):
    if file is not None:
        df = pd.read_csv(file)
    else:
        # Enhanced Default Data
        data = {
            "Visitor_Name": ["Ramesh", "Ramesh", "Suresh", "Suresh", "Suresh", "Amit", "Amit", "Amit", "Amit", "Vijay", "John", "John", "Priya"],
            "Inmate_ID": ["I-101", "I-102", "I-201", "I-202", "I-203", "I-101", "I-103", "I-104", "I-105", "I-201", "I-301", "I-302", "I-101"],
            "Visit_Date": ["2026-01-01", "2026-01-03", "2026-01-02", "2026-01-02", "2026-01-03", 
                           "2026-01-01", "2026-01-01", "2026-01-02", "2026-01-02", "2026-01-05",
                           "2026-01-04", "2026-01-04", "2026-01-06"],
            "Duration_Mins": [15, 20, 45, 30, 60, 120, 15, 20, 30, 10, 55, 40, 25]
        }
        df = pd.DataFrame(data)
    return df

df = load_data(uploaded_file)

# ---- AI: SUSPECT DETECTION LOGIC ----
visitor_counts = df['Visitor_Name'].value_counts()
frequent_visitors = visitor_counts[visitor_counts >= 3].index.tolist()

df['Date'] = pd.to_datetime(df['Visit_Date'])
daily_multi = df.groupby(['Visitor_Name', 'Date'])['Inmate_ID'].nunique()
suspicious_daily = daily_multi[daily_multi >= 2].index.get_level_values(0).unique().tolist()

# Combine suspects
suspects = list(set(frequent_visitors + suspicious_daily))
risk_level = "LOW"
if len(suspects) >= 3:
    risk_level = "HIGH"
elif len(suspects) >= 1:
    risk_level = "MEDIUM"

# ---- MAIN DASHBOARD ----
# Row 1: Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Visitors</div>
        <div class="metric-value">{df['Visitor_Name'].nunique()}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Inmates</div>
        <div class="metric-value">{df['Inmate_ID'].nunique()}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Visits</div>
        <div class="metric-value">{len(df)}</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    badge = 'risk-high' if risk_level == "HIGH" else ('risk-mid' if risk_level == "MEDIUM" else 'risk-low')
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: {'#dc3545' if risk_level=='HIGH' else '#ffc107' if risk_level=='MEDIUM' else '#28a745'};">
        <div class="metric-label">Security Alert Level</div>
        <div class="metric-value"><span class="{badge}">{risk_level}</span></div>
    </div>
    """, unsafe_allow_html=True)

# ---- TABS ----
tab1, tab2, tab3, tab4 = st.tabs(["📋 Visitor Logs", "🚨 Intelligence (Suspects)", "📸 AI Face Detector", "🕸️ Connection Map"])

with tab1:
    st.subheader("Visitor Registry")
    st.dataframe(df, use_container_width=True, height=300)

with tab2:
    st.subheader("Suspicious Activity Report")
    if suspects:
        st.warning(f"🚨 {len(suspects)} Suspect(s) Flagged for Surveillance")
        for name in suspects:
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.image("https://img.icons8.com/fluency/48/000000/person-female.png" if name in ["Priya"] else "https://img.icons8.com/fluency/48/000000/person-male.png", width=40)
            with col_b:
                st.markdown(f"**{name}**")
                st.caption(f"🔹 Visits: {visitor_counts.get(name,0)} | 🔹 Linked Inmates: {df[df['Visitor_Name']==name]['Inmate_ID'].nunique()}")
                st.progress(min(1.0, visitor_counts.get(name,0)/5))
        st.markdown("---")
        st.caption("📌 *Recommended Action: Increase surveillance on these individuals during entry.*")
    else:
        st.success("✅ No anomalies detected. All visitor patterns are normal.")

with tab3:
    st.subheader("Live AI Surveillance & Face Match")
    st.markdown("**Visitor Check-In Kiosk** (Simulated AI Biometric)")
    
    col_cam, col_info = st.columns([2, 1])
    with col_cam:
        # Camera input using built-in Streamlit camera (simplest, no extra deps)
        img_file_buffer = st.camera_input("Capture Visitor Face")
        
        if img_file_buffer is not None:
            # Read image
            bytes_data = img_file_buffer.getvalue()
            img = Image.open(io.BytesIO(bytes_data))
            
            # Convert to OpenCV
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Load Haar Cascade for Face Detection (Built-in)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Draw rectangles
            for (x, y, w, h) in faces:
                cv2.rectangle(img_cv, (x, y), (x+w, y+h), (0, 255, 0), 3)
                cv2.putText(img_cv, "Face Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
            
            # Display processed image
            st.image(img_cv, channels="BGR", caption="AI Processed Feed")
            
            # ---- DUMMY AI LOGIC ----
            if len(faces) > 0:
                # Mock risk scoring based on face count or random (just for demo)
                import random
                risk_score = random.randint(10, 95)
                st.markdown(f"**🧠 AI Analysis Result:**")
                if risk_score > 70:
                    st.error(f"⚠️ HIGH RISK MATCH! (Score: {risk_score}%) - Potential Blacklist Match!")
                    # If high risk, auto-add to suspects for demo purposes
                    if "CAM_SUSPECT" not in st.session_state:
                        st.session_state["CAM_SUSPECT"] = []
                    if len(st.session_state["CAM_SUSPECT"]) == 0:
                        st.session_state["CAM_SUSPECT"].append("Unknown_Cam_User")
                        st.warning("🚨 Added to real-time suspect list!")
                elif risk_score > 40:
                    st.warning(f"⚠️ MEDIUM RISK (Score: {risk_score}%) - Further verification required.")
                else:
                    st.success(f"✅ LOW RISK (Score: {risk_score}%) - Clear.")
            else:
                st.warning("❌ No face detected. Please ensure proper lighting.")
            
    with col_info:
        st.markdown("#### 📋 Visitor Profile")
        st.text_input("Full Name", placeholder="Enter Name")
        st.text_input("Aadhar (Last 4)", placeholder="XXXX", type="password")
        st.selectbox("Purpose", ["Legal Meeting", "Family Visit", "Material Handover"])
        if st.button("✅ Check-in & Run AI Scan"):
            st.success("Biometric scan queued. Check camera feed.")

with tab4:
    st.subheader("Network Intelligence Graph")
    fig, ax = plt.subplots(figsize=(12, 6))
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['Visitor_Name'], row['Inmate_ID'])
    
    color_map = []
    for node in G.nodes():
        if node in suspects:
            color_map.append('red')
        elif node.startswith('I-'):
            color_map.append('#0B4F6C') # Govt Blue
        else:
            color_map.append('#FF9933') # Saffron
    
    pos = nx.spring_layout(G, seed=42, k=0.5)
    nx.draw(G, with_labels=True, node_color=color_map, node_size=1500, 
            font_size=9, font_weight='bold', ax=ax, pos=pos, edge_color='gray', width=1.5)
    plt.tight_layout()
    st.pyplot(fig)
    st.caption("🔴 Red = Suspect | 🟠 Orange = Visitor | 🔵 Blue = Inmate")

# ---- FOOTER ----
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption("© 2026 BPR&D, Ministry of Home Affairs")
with col_f2:
    st.caption("🔒 Secured by Government of India Cyber Protocols")
with col_f3:
    st.caption("📍 Version 2.0 | AI Surveillance Active")
