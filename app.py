import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from io import StringIO

# ---- पेज का टाइटल ----
st.set_page_config(page_title="NETRA - Jail Visitor Analyzer", layout="wide")
st.title("🔍 NETRA - जेल विजिटर इंटेलिजेंस सिस्टम")

# ---- अगर कोई फाइल अपलोड नहीं होती, तो डमी डेटा बनाओ ----
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        # डमी डेटा (बिना पैसे के, सिर्फ दिमाग से बनाया)
        data = {
            "Visitor_Name": ["Ramesh", "Ramesh", "Suresh", "Suresh", "Suresh", "Amit", "Amit", "Amit", "Amit", "Vijay"],
            "Inmate_ID": ["I-101", "I-102", "I-201", "I-202", "I-203", "I-101", "I-103", "I-104", "I-105", "I-201"],
            "Visit_Date": ["2026-01-01", "2026-01-03", "2026-01-02", "2026-01-02", "2026-01-03", 
                           "2026-01-01", "2026-01-01", "2026-01-02", "2026-01-02", "2026-01-05"],
            "Duration_Mins": [15, 20, 45, 30, 60, 120, 15, 20, 30, 10]
        }
        df = pd.DataFrame(data)
    return df

# ---- साइडबार में फाइल अपलोडर ----
with st.sidebar:
    st.header("📂 डेटा अपलोड करें")
    uploaded_file = st.file_uploader("CSV फाइल डालें", type=['csv'])
    if uploaded_file:
        st.success("फाइल लोड हो गई!")

# डेटा लोड करो
df = load_data(uploaded_file)

# ---- 1. डेटा दिखाओ ----
st.subheader("📋 विजिटर लॉग")
st.dataframe(df, use_container_width=True)

# ---- 2. AI लॉजिक (रेड फ्लैग) ----
st.subheader("🚨 संदिग्ध विजिटर (रेड फ्लैग)")

# हर विजिटर की गणना
visitor_counts = df['Visitor_Name'].value_counts()
frequent_visitors = visitor_counts[visitor_counts >= 3].index.tolist()

# एक ही दिन में कई कैदियों से मिलने वाले
df['Date'] = pd.to_datetime(df['Visit_Date'])
daily_multi = df.groupby(['Visitor_Name', 'Date'])['Inmate_ID'].nunique()
suspicious_daily = daily_multi[daily_multi >= 3].index.get_level_values(0).unique().tolist()

# सारे संदिग्धों को मिलाओ
suspects = list(set(frequent_visitors + suspicious_daily))

if suspects:
    st.warning(f"⚠️ {len(suspects)} संदिग्ध विजिटर मिले:")
    for name in suspects:
        st.write(f"- **{name}** (इनकी गतिविधियां असामान्य हैं)")
else:
    st.success("✅ कोई संदिग्ध नहीं मिला!")

# ---- 3. ग्राफ (नेटवर्क) बनाओ ----
st.subheader("🕸️ विजिटर-कैदी कनेक्शन ग्राफ")

fig, ax = plt.subplots(figsize=(10, 6))
G = nx.Graph()

# ग्राफ में नोड्स और एजेस जोड़ो
for _, row in df.iterrows():
    G.add_edge(row['Visitor_Name'], row['Inmate_ID'])

# रंग सेट करो: संदिग्ध लाल, बाकी हरा
color_map = []
for node in G.nodes():
    if node in suspects:
        color_map.append('red')
    elif node.startswith('I-'):
        color_map.append('skyblue')
    else:
        color_map.append('green')

nx.draw(G, with_labels=True, node_color=color_map, node_size=800, 
        font_size=8, ax=ax, pos=nx.spring_layout(G, seed=42))
st.pyplot(fig)

# ---- 4. साइडबार में आंकड़े ----
st.sidebar.markdown("---")
st.sidebar.metric("कुल विजिटर्स", df['Visitor_Name'].nunique())
st.sidebar.metric("कुल कैदी", df['Inmate_ID'].nunique())
st.sidebar.metric("कुल मुलाकातें", len(df))
