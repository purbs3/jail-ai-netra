import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import io
import random

# ---- PAGE CONFIG ----
st.set_page_config(page_title="NETRA - BPR&D", layout="wide")

# ---- CUSTOM CSS: प्रोफेशनल सॉफ्टवेयर थीम ----
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    body, .stApp {
        font-family: 'Segoe UI', Roboto, Arial, sans-serif;
        background-color: #f4f7fc;
    }

    /* ----- HEADER ----- */
    .gov-header {
        background: white;
        padding: 0.6rem 1.5rem;
        border-bottom: 4px solid #0B4F6C;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
    }
    .gov-header-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }
    .gov-title {
        font-weight: 700;
        font-size: 1.3rem;
        color: #1a1a1a;
        margin: 0;
    }
    .gov-title span {
        color: #0B4F6C;
        font-weight: 800;
        letter-spacing: 1px;
    }
    .gov-badge {
        background: #0B4F6C;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .tricolor-line {
        height: 4px;
        background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 33%, #138808 66%);
        margin-top: 6px;
        border-radius: 2px;
    }

    /* ----- SIDEBAR NAVIGATION (Radio बटन को स्टाइल) ----- */
    /* Radio के डिफॉल्ट लेबल को हटाओ */
    .stRadio > div {
        flex-direction: column !important;
        gap: 2px !important;
    }
    /* हर ऑप्शन को Nav Item जैसा बनाओ */
    .stRadio label {
        padding: 10px 15px !important;
        margin: 2px 0 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        color: #3d4b5a !important;
        background: transparent !important;
        border-left: 3px solid transparent !important;
        transition: 0.2s !important;
        cursor: pointer !important;
    }
    /* होवर इफेक्ट */
    .stRadio label:hover {
        background: #f0f3f7 !important;
    }
    /* सिलेक्टेड (Active) ऑप्शन */
    .stRadio label[data-checked="true"] {
        background: #e8f0fe !important;
        color: #0B4F6C !important;
        border-left: 3px solid #0B4F6C !important;
        font-weight: 600 !important;
    }
    /* Radio के बुलेट पॉइंट्स (Circle) को हटाओ */
    .stRadio label > div:first-child {
        display: none !important;
    }

    /* Sidebar ब्रांडिंग */
    .sidebar-logo {
        padding: 10px 0 15px 0;
        border-bottom: 1px solid #e6e9ef;
        margin-bottom: 15px;
    }
    .sidebar-logo .app-name {
        font-size: 24px;
        font-weight: 800;
        color: #0B4F6C;
        letter-spacing: 1px;
    }
    .sidebar-logo .app-version {
        font-size: 12px;
        color: #7b8a9b;
        font-weight: 500;
    }
    .nav-divider {
        height: 1px;
        background: #e6e9ef;
        margin: 15px 0;
    }
    .sys-status {
        background: #f8fafc;
        padding: 10px 12px;
        border-radius: 8px;
        border: 1px solid #e6e9ef;
        font-size: 13px;
    }
    .status-dot-green { display: inline-block; width: 8px; height: 8px; background: #22c55e; border-radius: 50%; margin-right: 6px; }
    .status-dot-red { display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; margin-right: 6px; }
    .status-dot-yellow { display: inline-block; width: 8px; height: 8px; background: #eab308; border-radius: 50%; margin-right: 6px; }
    
    .user-profile {
        background: white;
        border: 1px solid #e6e9ef;
        border-radius: 30px;
        padding: 6px 12px 6px 8px;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 10px;
    }
    .user-avatar {
        width: 32px;
        height: 32px;
        background: #0B4F6C;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 14px;
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 18px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-left: 5px solid #0B4F6C;
        margin: 5px 0;
        transition: 0.2s;
    }
    .metric-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
    .metric-value { font-size: 2.1rem; font-weight: 700; color: #0B4F6C; line-height: 1.2; }
    .metric-label { font-size: 0.75rem; color: #6b7a8a; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }

    .risk-badge { padding: 2px 16px; border-radius: 20px; font-weight: 700; font-size: 0.9rem; }
    .risk-high { background: #fee2e2; color: #dc2626; }
    .risk-mid { background: #fef9c3; color: #ca8a04; }
    .risk-low { background: #dcfce7; color: #16a34a; }
    
    .footer-text { font-size: 0.75rem; color: #8a9aa8; text-align: center; border-top: 1px solid #e6e9ef; padding-top: 15px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
#  1. HEADER
# ==========================================
st.markdown("""
<div class="gov-header">
    <div class="gov-header-top">
        <div>
            <div style="display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap;">
                <div class="gov-title">भारत सरकार <span>| NETRA</span></div>
                <div style="font-size: 0.8rem; color: #4a5a6a;">Ministry of Home Affairs</div>
            </div>
            <div style="font-size: 0.85rem; color: #0B4F6C; font-weight: 500; margin-top: 2px;">
                National Extremity Tracking & Response Analytics
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 15px;">
            <span class="gov-badge">BPR&D v2.1</span>
            <span style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #3d5a6a;">
                <span class="status-dot-green"></span> Live
            </span>
        </div>
    </div>
    <div class="tricolor-line"></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
#  2. SIDEBAR (इंटरैक्टिव नेविगेशन)
# ==========================================
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="sidebar-logo">
        <div class="app-name">NETRA</div>
        <div class="app-version">Bureau of Police Research & Development</div>
        <div style="font-size: 11px; color: #8a9aa8; margin-top: 2px;">Secure Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    # ---- यहाँ MAGIC है: Clickable Navigation Menu ----
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #8a9aa8; text-transform: uppercase; letter-spacing: 0.5px; padding: 0 5px; margin-bottom: 8px;">Navigation</div>
    """, unsafe_allow_html=True)
    
    # Radio बटन: जिस पर क्लिक करेंगे, वही Page खुलेगा
    page = st.radio(
        label="Menu",  # Label को CSS से हटा दिया है
        options=["Dashboard", "Visitor Intelligence", "Biometric Scan", "Network Analysis"],
        index=0,
        key="nav_page",
        label_visibility="collapsed"  # लेबल को पूरी तरह छिपाओ
    )

    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

    # System Health
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #8a9aa8; text-transform: uppercase; letter-spacing: 0.5px; padding: 0 5px; margin-bottom: 8px;">System Health</div>
    <div class="sys-status">
        <div style="display: flex; justify-content: space-between; font-size: 13px;"><span>CPU Load</span> <span><span class="status-dot-green"></span> 34%</span></div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-top: 4px;"><span>Memory</span> <span><span class="status-dot-yellow"></span> 72%</span></div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-top: 4px;"><span>Uptime</span> <span>14h 23m</span></div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-top: 4px;"><span>AI Engine</span> <span><span class="status-dot-green"></span> Active</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

    # File Uploader
    uploaded_file = st.file_uploader("Import Visitor Log (CSV)", type=['csv'], label_visibility="collapsed")
    st.markdown("""
    <div style="margin-top: 10px; font-size: 12px; color: #6b7a8a; text-align: center; border-top: 1px solid #e6e9ef; padding-top: 15px;">
        <div style="font-weight:600; font-size:11px;">QUICK ACTIONS</div>
        <div style="display: flex; gap: 6px; justify-content: center; margin-top: 5px; flex-wrap: wrap;">
            <span style="background: #f0f3f7; padding: 2px 10px; border-radius: 12px; font-size: 11px;">New Check-in</span>
            <span style="background: #f0f3f7; padding: 2px 10px; border-radius: 12px; font-size: 11px;">Gen Report</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # User Profile
    st.markdown("""
    <div class="user-profile">
        <div class="user-avatar">AK</div>
        <div>
            <div style="font-weight: 600; font-size: 14px; line-height: 1.2;">Amit Kumar</div>
            <div style="font-size: 11px; color: #6b7a8a;">Superintendent (Admin)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
#  3. DATA LOADING (डेटा सब जगह काम आएगा)
# ==========================================
@st.cache_data
def load_data(file):
    if file is not None:
        df = pd.read_csv(file)
    else:
        data = {
            "Visitor_Name": ["Ramesh", "Ramesh", "Suresh", "Suresh", "Suresh", "Amit", "Amit", "Amit", "Amit", "Vijay", "John", "Priya"],
            "Inmate_ID": ["I-101", "I-102", "I-201", "I-202", "I-203", "I-101", "I-103", "I-104", "I-105", "I-201", "I-301", "I-101"],
            "Visit_Date": ["2026-01-01", "2026-01-03", "2026-01-02", "2026-01-02", "2026-01-03", 
                           "2026-01-01", "2026-01-01", "2026-01-02", "2026-01-02", "2026-01-05",
                           "2026-01-04", "2026-01-06"],
            "Duration_Mins": [15, 20, 45, 30, 60, 120, 15, 20, 30, 10, 55, 25]
        }
        df = pd.DataFrame(data)
    return df

df = load_data(uploaded_file)

# ---- AI INTELLIGENCE LOGIC (सभी पेजों के लिए कॉमन) ----
visitor_counts = df['Visitor_Name'].value_counts()
frequent_visitors = visitor_counts[visitor_counts >= 3].index.tolist()
df['Date'] = pd.to_datetime(df['Visit_Date'])
daily_multi = df.groupby(['Visitor_Name', 'Date'])['Inmate_ID'].nunique()
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

# ==========================================
#  4. PAGE RENDER (जादू यहीं होता है)
# ==========================================

# ----- PAGE 1: DASHBOARD -----
if page == "Dashboard":
    st.markdown("<h2 style='font-weight:600; color:#1a1a1a;'>Executive Dashboard</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{df['Visitor_Name'].nunique()}</div><div class="metric-label">Total Visitors</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{df['Inmate_ID'].nunique()}</div><div class="metric-label">Total Inmates</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total Visits</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card" style="border-left-color: {'#dc2626' if risk_level=='HIGH' else '#ca8a04' if risk_level=='MEDIUM' else '#16a34a'};"><div class="metric-value"><span class="risk-badge {risk_class}">{risk_level}</span></div><div class="metric-label">Security Alert Level</div></div>""", unsafe_allow_html=True)
    
    st.subheader("Recent Visitor Activity")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.caption("Dashboard refreshes automatically on data update.")

# ----- PAGE 2: VISITOR INTELLIGENCE -----
elif page == "Visitor Intelligence":
    st.markdown("<h2 style='font-weight:600; color:#1a1a1a;'>Visitor Intelligence Unit</h2>", unsafe_allow_html=True)
    
    tab_logs, tab_suspects = st.tabs(["All Logs", "Flagged Suspects"])
    with tab_logs:
        st.dataframe(df, use_container_width=True)
    with tab_suspects:
        if suspects:
            st.warning(f"ALERT: {len(suspects)} suspect(s) flagged for surveillance.")
            for name in suspects:
                col_a, col_b = st.columns([1, 4])
                with col_a:
                    st.markdown(f"<div style='background:#dc2626; color:white; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold;'>!</div>", unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"**{name}**")
                    st.caption(f"Visits: {visitor_counts.get(name,0)} | Linked Inmates: {df[df['Visitor_Name']==name]['Inmate_ID'].nunique()}")
                    st.progress(min(1.0, visitor_counts.get(name,0)/5))
        else:
            st.success("All clear. No anomalies detected.")

# ----- PAGE 3: BIOMETRIC SCAN (AI Camera) -----
elif page == "Biometric Scan":
    st.markdown("<h2 style='font-weight:600; color:#1a1a1a;'>Biometric AI Surveillance</h2>", unsafe_allow_html=True)
    st.caption("Visitor Check-In Kiosk | AI Mock Server Active")
    
    col_cam, col_info = st.columns([2, 1])
    with col_cam:
        img_file_buffer = st.camera_input("Capture Visitor Face")
        if img_file_buffer is not None:
            img = Image.open(io.BytesIO(img_file_buffer.getvalue())).convert("RGB")
            draw = ImageDraw.Draw(img)
            width, height = img.size
            box_x1, box_y1, box_x2, box_y2 = int(width*0.25), int(height*0.25), int(width*0.75), int(height*0.75)
            draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline="#00FF00", width=4)
            draw.text((box_x1, box_y1-20), "FACE DETECTED", fill="#00FF00")
            risk_score = random.randint(15, 95)
            st.image(img, caption="AI Processed Feed", use_column_width=True)
            st.markdown("**AI Analysis Result**")
            if risk_score > 70:
                st.error(f"HIGH RISK MATCH! (Score: {risk_score}%)")
                if "CAM_SUSPECT" not in st.session_state:
                    st.session_state["CAM_SUSPECT"] = []
                if len(st.session_state["CAM_SUSPECT"]) == 0:
                    st.session_state["CAM_SUSPECT"].append("Unknown_Cam_User")
                    st.warning("Added to real-time suspect list.")
            elif risk_score > 40:
                st.warning(f"MEDIUM RISK (Score: {risk_score}%)")
            else:
                st.success(f"LOW RISK (Score: {risk_score}%)")
        else:
            st.info("Press 'Capture' to scan the visitor.")
    
    with col_info:
        st.markdown("#### Visitor Profile")
        st.text_input("Full Name", placeholder="Enter Name")
        st.text_input("Aadhar (Last 4)", placeholder="XXXX", type="password")
        st.selectbox("Purpose", ["Legal Meeting", "Family Visit", "Material Handover"])
        if st.button("AI Check-in"):
            st.success("Biometric scan queued.")

# ----- PAGE 4: NETWORK ANALYSIS -----
elif page == "Network Analysis":
    st.markdown("<h2 style='font-weight:600; color:#1a1a1a;'>Network Intelligence Graph</h2>", unsafe_allow_html=True)
    st.caption("Visualizing connections between Visitors and Inmates.")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['Visitor_Name'], row['Inmate_ID'])
    color_map = ['#dc2626' if node in suspects else ('#0B4F6C' if node.startswith('I-') else '#FF9933') for node in G.nodes()]
    nx.draw(G, with_labels=True, node_color=color_map, node_size=1500, 
            font_size=9, font_weight='bold', pos=nx.spring_layout(G, seed=42))
    st.pyplot(fig)
    st.caption("Node Legend: Red = Suspect | Saffron = Visitor | Dark Blue = Inmate")

# ==========================================
#  5. FOOTER
# ==========================================
st.markdown("""
<div class="footer-text">
    (C) 2026 Bureau of Police Research & Development, Ministry of Home Affairs. 
    <span style="color: #0B4F6C;">|</span> Secure Intelligence Platform v2.1 
    <span style="color: #0B4F6C;">|</span> All rights reserved.
</div>
""", unsafe_allow_html=True)
