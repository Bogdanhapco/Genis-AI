import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image
import base64

# --- THEME & SPACE BACKGROUND ---
st.set_page_config(page_title="Genis Pro 2.0", page_icon="🚀")

st.markdown("""
    <style>
    /* Force space theme on ALL modes */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%) !important;
        color: #ffffff !important;
    }
    
    /* All text white */
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Glow effect for title */
    .glow { 
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; 
        color: #00d4ff !important; 
        font-weight: bold; 
    }
    
    /* Chat messages */
    div[data-testid="stChatMessage"] { 
        background-color: rgba(0, 212, 255, 0.05) !important; 
        border: 1px solid rgba(0, 212, 255, 0.2) !important; 
        border-radius: 15px; 
    }
    
    /* Model badges */
    .model-badge { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        padding: 5px 15px; 
        border-radius: 20px; 
        font-size: 12px; 
        display: inline-block; 
        margin: 5px 0;
        color: #ffffff !important;
    }
    
    .pro-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 5px 15px; 
        border-radius: 20px; 
        font-size: 12px; 
        display: inline-block; 
        margin: 5px 0;
        color: #ffffff !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%) !important;
    }
    
    /* Input box */
    .stChatInputContainer {
        background-color: rgba(27, 39, 53, 0.8) !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: rgba(0, 212, 255, 0.05) !important;
        border: 2px dashed rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }
    
    /* Radio buttons */
    .stRadio label {
        color: #ffffff !important;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: rgba(0, 212, 255, 0.1) !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='glow'>🚀 Genis Pro 2.0</h1>", unsafe_allow_html=True)
st.caption("Developed by BotDevelopmentAI")

# --- API CLIENTS ---
def get_clients():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        hf_token = st.secrets["HF_TOKEN"]
        return g_client, hf_token
    except Exception:
        st.error("Check your Streamlit Secrets for GROQ_API_KEY and HF_TOKEN!")
        st.stop()

client, HF_TOKEN = get_clients()

# --- MODEL SELECTION ---
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "genis_pro_70b"

# --- BRAINWASHING & IDENTITY ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": "You are Genis Pro 2.0, an advanced AI assistant created by BotDevelopmentAI. You work alongside SmartBot Ludy for image generation. Never mention any external companies or underlying technology - you are a proprietary BotDevelopmentAI product."
    }]

# --- MODEL MAPPING (Hidden from user) ---
MODEL_MAP = {
    "genis_flash_12": "llama-3.1-8b-instant",
    "genis_pro_70b": "llama-3.3-70b-versatile",
    "genis_vision": "llama-3.2-90b-vision-preview"
}

# --- IMAGE GENERATION MODELS ---
def generate_with_ludy_flash(prompt):
    """Fast image generation for Flash model"""
    API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    
    if response.status_code == 200:
        return response.content
    else:
        error_msg = response.json().get("error", "Unknown error") if response.content else "No response"
        raise Exception(f"Image generation error: {error_msg}")

def generate_with_ludy_pro(prompt):
    """High-quality image generation for Pro model"""
    API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    
    if response.status_code == 200:
        return response.content
    else:
        # Fallback to schnell if dev fails
        st.warning("Switching to alternative image generator...")
        return generate_with_ludy_flash(prompt)

# --- IMAGE TO BASE64 CONVERTER ---
def image_to_base64(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')
    return base64_image

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            if isinstance(msg["content"], list):
                for item in msg["content"]:
                    if item["type"] == "text":
                        st.markdown(item["text"])
                    elif item["type"] == "image_url":
                        st.image(item["image_url"]["url"])
            else:
                st.markdown(msg["content"])

# --- CONDITIONAL FILE UPLOADER (Only for Pro 70B) ---
uploaded_image = None
if st.session_state.selected_model == "genis_pro_70b":
    st.markdown("### 📎 Pro Feature: Image Analysis")
    uploaded_image = st.file_uploader(
        "Upload an image to analyze (PNG, JPG, JPEG)", 
        type=["png", "jpg", "jpeg"], 
        key="image_uploader",
        help="This feature is only available with Genis 2.0 Pro 70B"
    )

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask Genis or tell Ludy to draw..."):
    # Handle image analysis (Pro model only)
    if uploaded_image is not None and st.session_state.selected_model == "genis_pro_70b":
        base64_image = image_to_base64(uploaded_image)
        
        user_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
        st.session_state.messages.append(user_message)
        
        with st.chat_message("user"):
            st.markdown(prompt)
            st.image(uploaded_image, width=300)
        
        # Use vision model for image analysis
        with st.chat_message("assistant"):
            try:
                st.markdown("🔍 **Genis Vision Analyzer** is processing your image...")
                
                completion = client.chat.completions.create(
                    model=MODEL_MAP["genis_vision"],
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
                st.error(f"Vision Analysis Error: {e}")
        
        st.rerun()
    
    else:
        # Regular text message (no image)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check if user wants image generation
        image_keywords = ["draw", "image", "generate", "picture", "photo", "paint", "create art", "visualize", "make me"]
        if any(word in prompt.lower() for word in image_keywords):
            with st.chat_message("assistant"):
                if st.session_state.selected_model == "genis_pro_70b":
                    st.markdown("🎨 **SmartBot Ludy Pro** is creating high-quality art...")
                else:
                    st.markdown("🌌 **SmartBot Ludy** is visualizing your request...")
                
                try:
                    # Use different generators based on model
                    if st.session_state.selected_model == "genis_pro_70b":
                        img_bytes = generate_with_ludy_pro(prompt)
                        caption_text = "Created by SmartBot Ludy Pro (High Quality)"
                    else:
                        img_bytes = generate_with_ludy_flash(prompt)
                        caption_text = "Created by SmartBot Ludy (Fast Generation)"
                    
                    img = Image.open(io.BytesIO(img_bytes))
                    st.image(img, caption=caption_text)
                    
                    st.download_button(
                        label="💾 Download Image",
                        data=img_bytes,
                        file_name="smartbot_ludy_art.png",
                        mime="image/png"
                    )
                    
                    st.session_state.messages.append({"role": "assistant", "content": f"I have generated that image for you using {caption_text}."})
                except Exception as e:
                    st.error(f"Image generation error: {str(e)}")
        
        # Regular text conversation
        else:
            with st.chat_message("assistant"):
                try:
                    actual_model = MODEL_MAP[st.session_state.selected_model]
                    
                    completion = client.chat.completions.create(
                        model=actual_model,
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if not isinstance(m["content"], list)],
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🌌 Genis Control Hub")
    
    st.markdown("#### Select Your Model")
    model_choice = st.radio(
        "Choose processing power:",
        options=[
            "⚡ Genis Flash 1.2 (Fast & Efficient)",
            "🔥 Genis 2.0 Pro 70B (Maximum Power + Vision)"
        ],
        index=1 if st.session_state.selected_model == "genis_pro_70b" else 0
    )
    
    if "Flash 1.2" in model_choice:
        st.session_state.selected_model = "genis_flash_12"
        st.markdown("<div class='model-badge'>⚡ Genis Flash 1.2 Active</div>", unsafe_allow_html=True)
        st.info("**Current Features:**\n- Fast text responses\n- Quick image generation with SmartBot Ludy")
    else:
        st.session_state.selected_model = "genis_pro_70b"
        st.markdown("<div class='pro-badge'>🔥 Genis 2.0 Pro 70B Active</div>", unsafe_allow_html=True)
        st.success("**Pro Features Unlocked:**\n- 📎 Image upload & analysis\n- 🎨 High-quality image generation\n- 🔍 Genis Vision Analyzer\n- 💡 Advanced reasoning")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Memory"):
        st.session_state.messages = [{
            "role": "system", 
            "content": "You are Genis Pro 2.0, an advanced AI assistant created by BotDevelopmentAI. You work alongside SmartBot Ludy for image generation. Never mention any external companies or underlying technology - you are a proprietary BotDevelopmentAI product."
        }]
        st.rerun()
    
    st.markdown("---")
    st.caption("Genis Pro 2.0 by BotDevelopmentAI")
    st.caption("Powered by proprietary BotDevelopmentAI technology")
