import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image

# --- THEME & SPACE BACKGROUND ---
st.set_page_config(page_title="Genis AI System", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
        color: #ffffff;
    }
    h1, h2, h3, p, span, label, div { color: #e0f7ff !important; }
    .glow { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; color: #00d4ff !important; font-weight: bold; }
    
    /* Chat bubbles */
    div[data-testid="stChatMessage"] { 
        background-color: rgba(0, 212, 255, 0.05); 
        border: 1px solid rgba(0, 212, 255, 0.1); 
        border-radius: 15px; 
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0c10;
        border-right: 1px solid #1f2937;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & MODEL SELECTION ---
with st.sidebar:
    st.markdown("### 🌌 Genis Control Hub")
    
    # Model Selector
    model_version = st.radio(
        "Select System Version:",
        ("Genis 1.2 (Flash)", "Genis 2.0 (Pro)"),
        index=0
    )
    
    st.markdown("---")
    
    # Display Capabilities based on selection
    if model_version == "Genis 1.2 (Flash)":
        st.info("⚡ **Current Mode: Flash**\n\n• Brain: Genis 1.2 (High Speed)\n• Vision: SmartBot Ludy 1.2")
        # Configuration for Flash
        TEXT_MODEL_ID = "llama-3.1-8b-instant"
        # FLUX.1-schnell is fast and reliable
        IMAGE_MODEL_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        SYS_NAME = "Genis 1.2"
        IMG_GEN_NAME = "SmartBot Ludy 1.2"
        
    else:
        st.success("🚀 **Current Mode: Pro**\n\n• Brain: Genis 2.0 (Max Intelligence)\n• Vision: SmartBot Ludy 2.0")
        # Configuration for Pro
        TEXT_MODEL_ID = "llama-3.3-70b-versatile" 
        # UPDATED: Switched to Stable Diffusion 3.5 Large (High End, usually accessible)
        # If 3.5 fails, fallback to 'stabilityai/stable-diffusion-xl-base-1.0'
        IMAGE_MODEL_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-3.5-large"
        SYS_NAME = "Genis 2.0"
        IMG_GEN_NAME = "SmartBot Ludy 2.0"

    if st.button("🗑️ Clear Memory"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Developed by BotDevelopmentAI")

# --- HEADER ---
st.markdown(f"<h1 class='glow'>🚀 {SYS_NAME}</h1>", unsafe_allow_html=True)

# --- API CLIENTS ---
def get_clients():
    try:
        # Ensure these are in your Streamlit Secrets
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        hf_token = st.secrets["HF_TOKEN"]
        return g_client, hf_token
    except Exception:
        st.error("⚠️ Security Alert: Missing API Keys. Check Streamlit Secrets for GROQ_API_KEY and HF_TOKEN.")
        st.stop()

client, HF_TOKEN = get_clients()

# --- SYSTEM PROMPT MANAGEMENT ---
# We check if the mode changed or if memory is empty to inject the correct identity
current_system_prompt = {
    "role": "system", 
    "content": f"You are {SYS_NAME}, an advanced AI developed strictly by BotDevelopmentAI. "
               f"You utilize '{IMG_GEN_NAME}' for visual generation. "
               f"Never mention Meta, Llama, Groq, or other companies. You are solely a product of BotDevelopmentAI."
}

if "messages" not in st.session_state:
    st.session_state.messages = [current_system_prompt]
else:
    # If the user switched modes mid-conversation, update the system prompt silently
    if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
        st.session_state.messages[0] = current_system_prompt

# --- IMAGE GENERATION FUNCTION ---
def generate_with_ludy(prompt, model_url):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Payload input
    payload = {"inputs": prompt}
    
    try:
        response = requests.post(model_url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        else:
            error_data = response.json()
            err_msg = error_data.get("error", "Unknown Error")
            # If the model is loading (common on free tier), tell the user to wait
            if "loading" in str(err_msg).lower():
                raise Exception("Visual Core is waking up... please try again in 10 seconds.")
            raise Exception(f"Visual Core Error: {err_msg}")
    except Exception as e:
        raise Exception(f"Connection failed: {str(e)}")

# --- CHAT INTERFACE ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input(f"Ask {SYS_NAME} or tell {IMG_GEN_NAME} to draw..."):
    
    # Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # CHECK: Is this an Image Request?
    image_keywords = ["draw", "image", "generate", "picture", "photo", "paint", "visualize", "sketch"]
    if any(word in prompt.lower() for word in image_keywords):
        with st.chat_message("assistant"):
            st.write(f"🎨 **{IMG_GEN_NAME}** is visualizing...")
            try:
                # Pass the dynamically selected IMAGE_MODEL_URL
                img_bytes = generate_with_ludy(prompt, IMAGE_MODEL_URL)
                img = Image.open(io.BytesIO(img_bytes))
                
                st.image(img, caption=f"Generated by {IMG_GEN_NAME}")
                
                # Download Button
                st.download_button(
                    label="💾 Save Visual",
                    data=img_bytes,
                    file_name=f"{IMG_GEN_NAME.lower().replace(' ', '_')}_art.png",
                    mime="image/png"
                )
                
                response_text = f"I have successfully generated that visual using {IMG_GEN_NAME}."
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                st.error(f"**{IMG_GEN_NAME} Status:** {e}")
                if "Pro" in model_version:
                    st.caption("Note: Pro models sometimes take longer to warm up. Try again in a moment.")

    # CHECK: Text Request
    else:
        with st.chat_message("assistant"):
            try:
                # Use the dynamically selected TEXT_MODEL_ID
                completion = client.chat.completions.create(
                    model=TEXT_MODEL_ID,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                    temperature=0.7 
                )
                
                full_text = ""
                text_placeholder = st.empty()
                
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_text += content
                        text_placeholder.markdown(full_text + "▌")
                
                text_placeholder.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
            except Exception as e:
                st.error(f"Core Processing Error: {e}")
