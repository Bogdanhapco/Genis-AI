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
    div[data-testid="stChatMessage"] { background-color: rgba(0, 212, 255, 0.05); border-radius: 15px; }
    section[data-testid="stSidebar"] { background-color: #0b0c10; border-right: 1px solid #1f2937; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & MODEL SELECTION ---
with st.sidebar:
    st.markdown("### 🌌 Genis Control Hub")
    model_version = st.radio("Select System Version:", ("Genis 1.2 (Flash)", "Genis 2.0 (Pro)"), index=1)
    
    st.markdown("---")
    
    if model_version == "Genis 1.2 (Flash)":
        st.info("⚡ **Flash Mode**\n• Brain: Genis 1.2\n• Vision: Ludy 1.2 (SDXL)")
        TEXT_MODEL_ID = "llama-3.1-8b-instant"
        # Flash: Stable Diffusion XL (Highly compatible)
        IMAGE_MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
        SYS_NAME, IMG_GEN_NAME = "Genis 1.2", "SmartBot Ludy 1.2"
    else:
        st.success("🚀 **Pro Mode**\n• Brain: Genis 2.0\n• Vision: Ludy 2.0 (FLUX)")
        TEXT_MODEL_ID = "llama-3.3-70b-versatile" 
        # Pro: FLUX.1-schnell (Best speed-to-quality ratio on router)
        IMAGE_MODEL_ID = "black-forest-labs/FLUX.1-schnell"
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
        st.error("Missing API Keys!")
        st.stop()

client, HF_TOKEN = get_clients()

# --- ROUTER IMAGE GENERATION ---
def generate_with_router(prompt, model_id):
    # This is the 2026 standardized router path for specific model inference
    url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    
    # Payload for image generation
    payload = {"inputs": prompt, "parameters": {"num_inference_steps": 4 if "flux" in model_id.lower() else 30}}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.content
    else:
        # Handle the common loading or not found errors
        try:
            err = response.json().get("error", "Unknown Router Error")
        except:
            err = f"Status Code {response.status_code}"
        raise Exception(err)

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

    if any(word in prompt.lower() for word in ["draw", "image", "generate", "visualize"]):
        with st.chat_message("assistant"):
            with st.spinner(f"🎨 {IMG_GEN_NAME} is routing your request..."):
                try:
                    img_bytes = generate_with_router(prompt, IMAGE_MODEL_ID)
                    st.image(Image.open(io.BytesIO(img_bytes)), caption=f"Visualized by {IMG_GEN_NAME}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Image generated via {IMG_GEN_NAME}."})
                except Exception as e:
                    st.error(f"Router Exception: {e}")
    else:
        # Text Logic
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model=TEXT_MODEL_ID,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )
                full_text = ""
                placeholder = st.empty()
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_text += chunk.choices[0].delta.content
                        placeholder.markdown(full_text + "▌")
                placeholder.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
            except Exception as e:
                st.error(f"Processing Error: {e}")
