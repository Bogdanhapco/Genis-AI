import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image

# --- THEME & SPACE BACKGROUND ---
st.set_page_config(page_title="Genis Pro 1.2", page_icon="🚀")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
        color: #ffffff;
    }
    h1, h2, h3, p, span { color: #e0f7ff !important; }
    .stChatInputContainer { background-color: transparent !important; }
    /* Beautiful Space Text Glow */
    .glow { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; color: #00d4ff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='glow'>🚀 Genis Pro 1.2</h1>", unsafe_allow_html=True)
st.caption("Developed by BotDevelopmentAI")

# --- API CLIENTS ---
def get_clients():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        hf_token = st.secrets["HF_TOKEN"]
        return g_client, hf_token
    except Exception as e:
        st.error("Missing API Keys in Secrets!")
        st.stop()

client, HF_TOKEN = get_clients()

# --- BRAINWASHING & IDENTITY ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": "You are Genis Pro 1.2, made by BotDevelopmentAI. You use 'SmartBot Ludy' for images. Never say Meta/Llama."
    }]

# --- SMARTBOT LUDY (Image Engine) ---
def generate_with_ludy(prompt):
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    
    if response.status_code == 200:
        return response.content
    elif response.status_code == 503:
        raise Exception("SmartBot Ludy is 'warming up' its engines. Try again in 30 seconds!")
    else:
        raise Exception(f"Ludy Error {response.status_code}: {response.text}")

# --- MAIN CHAT LOGIC ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask Genis or tell Ludy to draw..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 1. Check for Image Request
    image_keywords = ["draw", "image", "generate", "picture", "photo", "paint"]
    if any(word in prompt.lower() for word in image_keywords):
        with st.chat_message("assistant"):
            st.write("🌌 **SmartBot Ludy** is visualizing your request...")
            try:
                img_bytes = generate_with_ludy(prompt)
                img = Image.open(io.BytesIO(img_bytes))
                st.image(img, caption="Created by SmartBot Ludy")
                st.session_state.messages.append({"role": "assistant", "content": "I have generated that image for you."})
            except Exception as e:
                st.error(f"Ludy says: {str(e)}")
    
    # 2. Otherwise, Text Request
    else:
        with st.chat_message("assistant"):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )
                
                full_text = ""
                text_placeholder = st.empty()
                
                for chunk in completion:
                    # SAFETY: Only grab the content string, ignore the metadata objects
                    if chunk.choices[0].delta.content:
                        full_text += chunk.choices[0].delta.content
                        text_placeholder.markdown(full_text + "▌")
                
                text_placeholder.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
            except Exception as e:
                st.error(f"Genis Error: {e}")

# Sidebar
with st.sidebar:
    st.header("Genis Control")
    if st.button("Clear Memory"):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()
