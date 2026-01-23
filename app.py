import streamlit as st
from groq import Groq
import requests
import io
import time
from PIL import Image

# --- THEME & SPACE BACKGROUND ---
st.set_page_config(page_title="Genis AI System", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
        color: #ffffff;
    }
    h1, h2, h3, p, span, label, .stMarkdown { color: #e0f7ff !important; }
    .glow { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; color: #00d4ff !important; font-weight: bold; }
    div[data-testid="stChatMessage"] { background-color: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 15px; }
    section[data-testid="stSidebar"] { background-color: #0b0c10; border-right: 1px solid #1f2937; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & MODEL SELECTION ---
with st.sidebar:
    st.markdown("### 🌌 Genis Control Hub")
    model_version = st.radio("Select System Version:", ("Genis 1.2 (Flash)", "Genis 2.0 (Pro)"), index=1) # Default to Pro
    
    st.markdown("---")
    
    if model_version == "Genis 1.2 (Flash)":
        st.info("⚡ **Flash Mode**\n\n• Brain: Genis 1.2\n• Vision: SmartBot Ludy 1.2")
        TEXT_MODEL_ID = "llama-3.1-8b-instant"
        IMAGE_MODEL_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        SYS_NAME, IMG_GEN_NAME = "Genis 1.2", "SmartBot Ludy 1.2"
    else:
        st.success("🚀 **Pro Mode**\n\n• Brain: Genis 2.0 (Llama 3.3 70B)\n• Vision: SmartBot Ludy 2.0 (FLUX.2 Dev)")
        TEXT_MODEL_ID = "llama-3.3-70b-versatile" 
        # UPGRADED: Using FLUX.2 Dev for "Pro" quality
        IMAGE_MODEL_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev"
        SYS_NAME, IMG_GEN_NAME = "Genis 2.0", "SmartBot Ludy 2.0"

    if st.button("🗑️ Clear Memory"):
        st.session_state.messages = []
        st.rerun()

# --- API CLIENTS ---
def get_clients():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        hf_token = st.secrets["HF_TOKEN"]
        return g_client, hf_token
    except:
        st.error("Missing API Keys in Secrets!")
        st.stop()

client, HF_TOKEN = get_clients()

# --- INITIALIZE SYSTEM PROMPT ---
current_system_prompt = {
    "role": "system", 
    "content": f"You are {SYS_NAME} by BotDevelopmentAI. Use '{IMG_GEN_NAME}' for images. Never mention Meta/Llama."
}

if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [current_system_prompt]

# --- IMAGE GENERATION (With Auto-Retry) ---
def generate_with_ludy(prompt, model_url):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    for attempt in range(3): # Try 3 times if it's "loading"
        response = requests.post(model_url, headers=headers, json={"inputs": prompt})
        if response.status_code == 200:
            return response.content
        
        err = response.json().get("error", "")
        if "loading" in err.lower() or "estimated_time" in err.lower():
            time.sleep(5) # Wait for model to load
            continue
        raise Exception(err)
    raise Exception("Model took too long to load. Please try once more.")

# --- CHAT UI ---
st.markdown(f"<h1 class='glow'>🚀 {SYS_NAME}</h1>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input(f"Message {SYS_NAME}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    image_keywords = ["draw", "image", "generate", "picture", "photo", "visualize"]
    if any(word in prompt.lower() for word in image_keywords):
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown(f"🎨 **{IMG_GEN_NAME}** is generating high-fidelity art...")
            try:
                img_bytes = generate_with_ludy(prompt, IMAGE_MODEL_URL)
                placeholder.empty()
                st.image(Image.open(io.BytesIO(img_bytes)), caption=f"Created by {IMG_GEN_NAME}")
                st.session_state.messages.append({"role": "assistant", "content": f"Visual generated via {IMG_GEN_NAME}."})
            except Exception as e:
                st.error(f"Visual Core Error: {e}")
    else:
        with st.chat_message("assistant"):
            completion = client.chat.completions.create(
                model=TEXT_MODEL_ID,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            full_text = ""
            text_placeholder = st.empty()
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_text += chunk.choices[0].delta.content
                    text_placeholder.markdown(full_text + "▌")
            text_placeholder.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
