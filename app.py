import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image
import urllib.parse

# --- THEME & SPACE BACKGROUND ---
st.set_page_config(page_title="Genis Pro 1.2", page_icon="🚀")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
        color: #ffffff;
    }
    h1, h2, h3, p, span { color: #e0f7ff !important; }
    .glow { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; color: #00d4ff !important; font-weight: bold; }
    /* Style the chat bubbles for a space feel */
    div[data-testid="stChatMessage"] { background-color: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='glow'>🚀 Genis Pro 1.2</h1>", unsafe_allow_html=True)
st.caption("Developed by BotDevelopmentAI")

# --- API CLIENT (Only Groq needed now!) ---
def get_client():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        return g_client
    except Exception:
        st.error("Check your Streamlit Secrets for GROQ_API_KEY!")
        st.stop()

client = get_client()

# --- BRAINWASHING & IDENTITY ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": "You are Genis Pro 1.2, made by BotDevelopmentAI. You use 'SmartBot Ludy' for images. Never mention Meta or Llama."
    }]

# --- SMARTBOT LUDY (Free Image Generation) ---
def generate_with_ludy(prompt):
    """Generate image using Pollinations.ai - completely free, no API key needed"""
    try:
        # Encode the prompt for URL
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Pollinations.ai endpoint with Flux model for photorealistic results
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
        
        # Fetch the image
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        return response.content
    except Exception as e:
        raise Exception(f"Ludy encountered an error: {str(e)}")

# --- MAIN CHAT LOGIC ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask Genis or tell Ludy to draw..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 1. Image Request Logic
    image_keywords = ["draw", "image", "generate", "picture", "photo", "paint", "create"]
    if any(word in prompt.lower() for word in image_keywords):
        with st.chat_message("assistant"):
            st.write("🌌 **SmartBot Ludy** is visualizing your request...")
            try:
                img_bytes = generate_with_ludy(prompt)
                img = Image.open(io.BytesIO(img_bytes))
                st.image(img, caption="Created by SmartBot Ludy")
                
                # Add a download button for the user
                st.download_button(
                    label="💾 Download Image",
                    data=img_bytes,
                    file_name="smartbot_ludy_art.png",
                    mime="image/png"
                )
                
                st.session_state.messages.append({"role": "assistant", "content": "I have generated that image for you using SmartBot Ludy."})
            except Exception as e:
                st.error(f"Ludy says: {str(e)}")
    
    # 2. Text Request Logic (No Spam Version)
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
                    if chunk.choices[0].delta.content:
                        full_text += chunk.choices[0].delta.content
                        text_placeholder.markdown(full_text + "▌")
                
                text_placeholder.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
            except Exception as e:
                st.error(f"Genis Error: {e}")

# Sidebar
with st.sidebar:
    st.markdown("### 🌌 Genis Hub")
    st.info("Genis Pro 1.2 by BotDevelopmentAI")
    if st.button("Clear Memory"):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()
