import streamlit as st
from groq import Groq
import requests
import io
import random
import time
from PIL import Image
from streamlit_autorefresh import st_autorefresh
import urllib.parse

# --- GLOBAL THEME & SETUP ---
st.set_page_config(page_title="Genis Pro 1.2", page_icon="🚀", layout="wide")

# Custom CSS for the "Space Data Center" Look
st.markdown("""
    <style>
    .stApp { background: radial-gradient(ellipse at bottom, #090A0F 0%, #050505 100%); color: #ffffff; }
    .stChatMessage { background-color: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 15px; }
    .glow { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; color: #00d4ff !important; font-weight: bold; }
    .metric-card {
        background: rgba(0, 255, 204, 0.05);
        border: 1px solid #00ffcc;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- API CLIENTS ---
def get_client():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        return g_client
    except Exception:
        st.error("⚠️ API Key missing! Add GROQ_API_KEY to Streamlit Secrets.")
        st.stop()

client = get_client()

# --- FREE IMAGE GENERATION (Pollinations.ai) ---
def generate_image(prompt):
    """Generate image using Pollinations.ai - completely free, no API key needed"""
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content))
        return img
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")
        return None

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 class='glow'>🛰️ BotDevelopmentAI</h1>", unsafe_allow_html=True)
    page = st.radio("System Menu", ["🚀 Genis Pro 1.2 (Chat)", "📡 Data Center Status"])
    st.divider()
    if st.button("Clear App Memory"):
        st.session_state.messages = [{"role": "system", "content": "You are Genis Pro 1.2 by BotDevelopmentAI. Use SmartBot Ludy for images."}]
        st.rerun()

# --- PAGE 1: CHAT ENGINE ---
if page == "🚀 Genis Pro 1.2 (Chat)":
    st.markdown("<h1 class='glow'>Genis Pro 1.2</h1>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are Genis Pro 1.2 by BotDevelopmentAI. Use SmartBot Ludy for images."}]

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ask Genis or tell Ludy to draw..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Image Logic
        if any(word in prompt.lower() for word in ["draw", "image", "generate", "picture", "create"]):
            with st.chat_message("assistant"):
                st.write("🌌 **SmartBot Ludy** is visualizing...")
                img = generate_image(prompt)
                if img:
                    st.image(img, caption="Created by SmartBot Ludy")
                    st.session_state.messages.append({"role": "assistant", "content": f"Generated image: {prompt}"})
                else:
                    st.error("Ludy is busy. Try again soon!")
        
        # Text Logic
        else:
            with st.chat_message("assistant"):
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True
                )
                full_text = ""
                placeholder = st.empty()
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_text += chunk.choices[0].delta.content
                        placeholder.markdown(full_text + "▌")
                placeholder.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})

# --- PAGE 2: DATA CENTER ---
else:
    # Auto-refresh every 4 seconds
    st_autorefresh(interval=4000, key="status_refresh")
    
    st.markdown("<h1 class='glow'>Infrastructure Status</h1>", unsafe_allow_html=True)
    st.write(f"Last Scan: {time.strftime('%H:%M:%S')}")
    
    col1, col2, col3 = st.columns(3)
    lpu_load = round(random.uniform(8.0, 14.5), 1)
    gpu_load = round(random.uniform(18.0, 35.2), 1)
    
    with col1:
        st.markdown(f"<div class='metric-card'><h3>LPU LOAD</h3><h2>{lpu_load}%</h2><p>Genis Brain</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h3>GPU LOAD</h3><h2>{gpu_load}%</h2><p>Ludy Engine</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><h3>NODES</h3><h2>148/150</h2><p>Operational</p></div>", unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📡 Live Node Logs")
    st.code(f"[{time.strftime('%H:%M:%S')}] Node-Alpha: Packet routing success.\n[{time.strftime('%H:%M:%S')}] Cluster-Beta: GPU temp stable at 68°C.", language="bash")
