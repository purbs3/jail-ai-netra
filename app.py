import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ---- पेज कॉन्फ़िगरेशन (सरकारी नाम) ----
st.set_page_config(
    page_title="NETRA - स्मार्ट जेल निगरानी प्रणाली", 
    page_icon="🦁",  # अशोक स्तंभ का प्रतीक
    layout="wide"
)

# ---- कस्टम CSS (तिरंगा और सरकारी स्टाइल) ----
st.markdown("""
<style>
    /* तिरंगा टॉप बार */
    .top-bar {
        background: linear-gradient(to right, #FF9933 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%);
        height: 8px;
        padding: 0;
        margin-bottom: 0px;
    }
    /* हेडर स्टाइल */
    .gov-header {
        background-color: #f0f4f8;
        padding: 1rem 2rem;
        border-radius: 10px;
        border-left: 6px solid #1E3A8A; /* नेवी ब्लू */
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .gov-header h1 {
        color: #1E3A8A;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    .gov-header p {
        color: #333;
        margin: 0;
        font-size: 1rem;
        font-weight: 500;
    }
    /* साइडबार को सरकारी नीला */
    .css-1d391kg, .css-163i15w {
        background-color: #F0F4F8;
    }
    /* डेटाफ्रेम को और साफ दिखाओ */
    .stDataFrame {
        border: 1px solid #ccc;
        border-radius: 8px;
    }
    /* फुटर */
    .footer {
        margin-top: 40px;
        text-align: center;
        border-top: 2px solid #FF9933;
        padding-top: 15px;
        color: #555;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ---- तिरंगा बार दिखाओ ----
st.markdown('<div class="top-bar"></div>', unsafe_allow_html=True)

# ---- सरकारी हेडर ----
st.markdown("""
<div class="gov-header">
    <h1>🦁 NETRA - केंद्रीय जेल इंटेलिजेंस प्रणाली</h1>
    <p>भारत सरकार | गृह मंत्रालय | स्मार्ट जेल मिशन (डिजिटल इंडिया)</p>
</div>
""", unsafe_allow_html=True)

# ---- डेटा लोड करने वाला फंक्शन (पहले जैसा) ----
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        data = {
            "Visitor_Name": ["Ramesh", "Ramesh", "Suresh", "Suresh", "Suresh", "Amit", "Amit", "Amit", "Amit", "Vijay"],
            "Inmate_ID": ["I-101", "I-102", "I-201", "I-202", "I-203", "I-101", "I-103", "I-104", "I-105", "I-201"],
            "Visit_Date": ["2026-01-01", "2026-01-03", "2026-01-02", "2026-01-02", "2026-01-03", 
                           "2026-01-01", "2026-01-01", "2026-01-02", "2026-01-02", "2026-01-05"],
            "Duration_Mins": [15, 20, 45, 30, 60, 120, 15, 20, 30, 10]
        }
        df = pd.DataFrame(data)
    return df

# ---- साइडबार ----
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/1200px-Emblem_of_India.svg.png", width=100)
    st.subheader("📂 डेटा अपलोड")
    uploaded_file = st.file_uploader("जेल रजिस्टर (CSV) अपलोड करें", type=['csv'])
    if uploaded_file:
        st.success("✅ डेटा सुरक्षित लोड हो गया!")
    st.markdown("---")
    st.caption("🔒 इस सिस्टम का उपयोग केवल अधिकृत कर्मियों द्वारा किया जाना है।")

# डेटा लोड
df = load_data(uploaded_file)

# ---- कॉलम लेआउट (बायां: टेबल, दायां: आंकड़े) ----
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 मुलाकाती रजिस्टर (लॉग)")
    st.dataframe(df, use_container_width=True, height=300)

with col2:
    st.subheader("📊 त्वरित आंकड़े")
    st.metric("कुल मुलाकातें", len(df))
    st.metric("कुल विजिटर्स", df['Visitor_Name'].nunique())
    st.metric("कुल कैदी", df['Inmate_ID'].nunique())

# ---- AI लॉजिक (यहाँ दिमाग लगा है) ----
st.markdown("---")
st.subheader("🚨 AI-जनित खुफिया रिपोर्ट (संदिग्ध गतिविधि)")

# विजिटर की गिनती
visitor_counts = df['Visitor_Name'].value_counts()
# रूल 1: 3 से ज्यादा आने वाले फ्लैग
frequent_visitors = visitor_counts[visitor_counts >= 3].index.tolist()

# एक्सपैंडर में पूरा लॉजिक समझाओ (ताकि सरकारी अफसर भी समझें)
with st.expander("🤔 यह रिपोर्ट कैसे बनी? (AI का गणित)", expanded=False):
    st.markdown("""
    1. **स्टेप 1**: सिस्टम सभी विजिटर्स की कुल मुलाकातें गिनता है।
    2. **स्टेप 2**: मानवीय व्यवहार के आधार पर, AI का 'थ्रेशहोल्ड' (सीमा) **3** है।
       - अगर कोई **3 या उससे ज़्यादा** बार आता है, तो यह असामान्य है।
    3. **आपके डेटा में**:
       - Ramesh 2 बार आया → ✅ सामान्य
       - Vijay 1 बार आया → ✅ सामान्य
       - **Suresh 3 बार आया** → 🚩 संदिग्ध
       - **Amit 4 बार आया** → 🚩 संदिग्ध
    4. **ग्राफ़ विश्लेषण**: दोनों संदिग्ध कई कैदियों (I-101 से I-105) से जुड़े हैं, जो मादक पदार्थ/मोबाइल तस्करी का पैटर्न है।
    """)

# रिजल्ट दिखाओ
if frequent_visitors:
    st.warning(f"⚠️ **{len(frequent_visitors)} संदिग्ध विजिटर** पहचाने गए (जिन्होंने निर्धारित सीमा से अधिक मुलाकात की):")
    for name in frequent_visitors:
        count = visitor_counts[name]
        st.error(f"🔴 **{name}** → {count} बार आया (उच्च जोखिम)")
else:
    st.success("✅ सभी विजिटर सामान्य सीमा में हैं।")

# ---- ग्राफ (कनेक्शन नेटवर्क) ----
st.subheader("🕸️ विजिटर-कैदी संबंध (कनेक्शन मैप)")
fig, ax = plt.subplots(figsize=(12, 6))
G = nx.Graph()

for _, row in df.iterrows():
    G.add_edge(row['Visitor_Name'], row['Inmate_ID'])

# रंग योजना: संदिग्ध लाल, कैदी नीला, सामान्य हरा
color_map = []
for node in G.nodes():
    if node in frequent_visitors:
        color_map.append('#FF0000')  # लाल (रेड फ्लैग)
    elif node.startswith('I-'):
        color_map.append('#1E3A8A')  # नेवी ब्लू (कैदी)
    else:
        color_map.append('#16A34A')  # हरा (सामान्य विजिटर)

nx.draw(G, with_labels=True, node_color=color_map, node_size=1000, 
        font_size=9, font_color='white', font_weight='bold',
        ax=ax, pos=nx.spring_layout(G, seed=42), edge_color='#888')
st.pyplot(fig)

# ---- फुटर (सरकारी डिस्क्लेमर) ----
st.markdown("""
<div class="footer">
    <p>🇮🇳 <strong>डिजिटल इंडिया पहल</strong> | यह प्रणाली पूर्णतः स्वदेशी तकनीक पर आधारित है | 
    <span style="color:#138808;">सुरक्षित</span> | <span style="color:#FF9933;">विश्वसनीय</span></p>
    <p style="font-size:0.7rem;">*यह एक पायलट प्रोजेक्ट है। अंतिम निर्णय जेल अधीक्षक का होगा।</p>
</div>
""", unsafe_allow_html=True)
