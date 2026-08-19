import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import io
import random

st.set_page_config(page_title="NETRA - BPR&D | MHA", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 6px solid #0B4F6C;
        margin: 5px 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0B4F6C;
    }
    .risk-high { background-color: #dc3545; color: white; padding: 2px 12px; border-radius: 20px; }
    .risk-mid { background-color: #ffc107; color: black; padding: 2px 12px; border-radius: 20px; }
    .risk-low { background-color: #28a745; color: white; padding: 2px 12px; border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

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

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/justice.png", width=80)
    st.markdown("### 🛡️ Command Center")
    uploaded_file = st.file_uploader("📂 Upload Visitor Log (CSV)", type=['csv'])
    st.markdown("---")
    st.success("🟢 All Systems Operational")
    st.caption("v2.1 - AI Mock Surveillance Mode")

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

visitor_counts = df['Visitor_Name'].value_counts()
frequent_visitors = visitor_counts[visitor_counts >= 3].index.tolist()

df['Date'] = pd.to_datetime(df['Visit_Date'])
daily_multi = df.groupby(['Visitor_Name', 'Date'])['Inmate_ID'].nunique()
suspicious_daily = daily_multi[daily_multi >= 2].index.get_level_values(0).unique().tolist()

suspects = list(set(frequent_visitors + suspicious_daily))

if len(suspects) >= 3:
    risk_level = "HIGH"
elif len(suspects) >= 1:
    risk_level = "MEDIUM"
else:
    risk_level = "LOW"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""<div class="metric-card"><div class="metric-value">{df['Visitor_Name'].nunique()}</div>Total Visitors</div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="metric-card"><div class="metric-value">{df['Inmate_ID'].nunique()}</div>Total Inmates</div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="metric-card"><div class="metric-value">{len(df)}</div>Total Visits</div>""", unsafe_allow_html=True)

with col4:
    badge = 'risk-high' if risk_level == "HIGH" else ('risk-mid' if risk_level == "MEDIUM" else 'risk-low')
    st.markdown(f"""<div class="metric-card"><div class="metric-value"><span class="{badge}">{risk_level}</span></div>Alert Level</div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📋 Visitor Logs", "🚨 Intelligence (Suspects)", "📸 AI Face Detector", "🕸️ Connection Map"])

with tab1:
    st.subheader("Visitor Registry")
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Suspicious Activity Report")
    if suspects:
        st.warning(f"🚨 {len(suspects)} Suspect(s) Flagged")
        for name in suspects:
            st.markdown(f"- **{name}** (Visits: {visitor_counts.get(name,0)} | Linked Inmates: {df[df['Visitor_Name']==name]['Inmate_ID'].nunique()})")
            st.progress(min(1.0, visitor_counts.get(name,0)/5))
    else:
        st.success("✅ No anomalies detected.")

with tab3:
    st.subheader("Live AI Surveillance & Face Match")
    st.markdown("**Visitor Check-In Kiosk** *(Powered by Government AI Mock Server)*")
    
    col_cam, col_info = st.columns([2, 1])
    
    with col_cam:
        img_file_buffer = st.camera_input("Capture Visitor Face")
        
        if img_file_buffer is not None:
            img = Image.open(io.BytesIO(img_file_buffer.getvalue())).convert("RGB")
            
            draw = ImageDraw.Draw(img)
            width, height = img.size
            
            box_x1 = int(width * 0.25)
            box_y1 = int(height * 0.25)
            box_x2 = int(width * 0.75)
            box_y2 = int(height * 0.75)
            
            draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline="#00FF00", width=4)
            draw.text((box_x1, box_y1-20), "FACE DETECTED (AI)", fill="#00FF00")
            
            risk_score = random.randint(15, 95)
            
            st.image(img, caption="AI Processed Feed", use_column_width=True)
            
            st.markdown("**🧠 AI Analysis Result:**")
            if risk_score > 70:
                st.error(f"⚠️ HIGH RISK MATCH! (Score: {risk_score}%) - Potential Blacklist Match!")
                if "CAM_SUSPECT" not in st.session_state:
                    st.session_state["CAM_SUSPECT"] = []
                if len(st.session_state["CAM_SUSPECT"]) == 0:
                    st.session_state["CAM_SUSPECT"].append("Unknown_Cam_User")
                    st.warning("🚨 Added to real-time suspect list!")
            elif risk_score > 40:
                st.warning(f"⚠️ MEDIUM RISK (Score: {risk_score}%) - Verification required.")
            else:
                st.success(f"✅ LOW RISK (Score: {risk_score}%) - Clear.")
        else:
            st.info("📸 Press 'Capture' above to scan the visitor.")

    with col_info:
        st.markdown("#### 📋 Visitor Profile")
        st.text_input("Full Name", placeholder="Enter Name")
        st.text_input("Aadhar (Last 4)", placeholder="XXXX", type="password")
        if st.button("✅ AI Check-in"):
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
            color_map.append('#0B4F6C')
        else:
            color_map.append('#FF9933')
    
    nx.draw(G, with_labels=True, node_color=color_map, node_size=1500, font_size=9, font_weight='bold', pos=nx.spring_layout(G, seed=42))
    st.pyplot(fig)

st.markdown("---")
st.caption("(c) 2026 BPR&D, Ministry of Home Affairs | Secured by Cyber Protocols")
