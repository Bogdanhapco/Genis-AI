import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image
import time

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
        replicate_token = st.secrets.get("REPLICATE_API_TOKEN", None)
        return g_client, hf_token, replicate_token
    except Exception:
        st.error("Check your Streamlit Secrets for GROQ_API_KEY, HF_TOKEN, and REPLICATE_API_TOKEN!")
        st.stop()

client, HF_TOKEN, REPLICATE_TOKEN = get_clients()

# --- MODEL SELECTION ---
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "genis_pro_70b"

# --- BRAINWASHING & IDENTITY ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": "You are Genis 2.0 pro, an advanced AI assistant created by BotDevelopmentAI. You work alongside SmartBot Ludy for image generation. Never mention any external companies or underlying technology - you are a proprietary BotDevelopmentAI product."
    }]

# --- MODEL MAPPING (Hidden from user) ---
MODEL_MAP = {
    "genis_flash_12": "llama-3.1-8b-instant",
    "genis_pro_70b": "llama-3.3-70b-versatile"
}

# --- IMAGE GENERATION MODELS ---
def generate_with_ludy_flash(prompt):
    """Fast image generation for Flash model - FLUX Schnell via HF Router"""
    API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
    
    if response.status_code == 200:
        return response.content
    else:
        error_msg = response.json().get("error", "Unknown error") if response.content else "No response"
        raise Exception(f"Flash image error: {error_msg}")

def generate_with_ludy_pro(prompt):
    """Premium quality image generation - FLUX Pro via Replicate"""
    if not REPLICATE_TOKEN:
        st.error("REPLICATE_API_TOKEN not found in secrets! Please add it to use Pro image generation.")
        raise Exception("Replicate API token missing")
    
    # Start the prediction
    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Token {REPLICATE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "version": "39b3434f194ac0a1fc907ce8c9c42c0f3a25f89c76aeb83d4db5b7c6bb6d288b",  # FLUX Pro 1.1
            "input": {
                "prompt": prompt,
                "aspect_ratio": "1:1",
                "output_format": "png",
                "output_quality": 100,
                "safety_tolerance": 2
            }
        },
        timeout=10
    )
    
    if response.status_code != 201:
        raise Exception(f"Failed to start prediction: {response.text}")
    
    prediction = response.json()
    prediction_id = prediction["id"]
    
    # Poll for completion
    max_attempts = 60  # 60 seconds max wait
    for attempt in range(max_attempts):
        response = requests.get(
            f"https://api.replicate.com/v1/predictions/{prediction_id}",
            headers={"Authorization": f"Token {REPLICATE_TOKEN}"},
            timeout=10
        )
        
        prediction = response.json()
        status = prediction["status"]
        
        if status == "succeeded":
            # Download the image
            image_url = prediction["output"][0] if isinstance(prediction["output"], list) else prediction["output"]
            img_response = requests.get(image_url, timeout=30)
            return img_response.content
        elif status == "failed":
            raise Exception(f"Image generation failed: {prediction.get('error', 'Unknown error')}")
        
        time.sleep(1)
    
    raise Exception("Image generation timed out")

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask Genis or tell Ludy to draw..."):
    
    # Check if user wants image generation
    image_keywords = ["draw", "image", "generate", "picture", "photo", "paint", "create art", "visualize", "make me", "design"]
    is_image_generation = any(word in prompt.lower() for word in image_keywords)
    
    # Handle image generation
    if is_image_generation:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            if st.session_state.selected_model == "genis_pro_70b":
                st.markdown("🎨 **SmartBot Ludy 2.0 Ultra** is creating premium quality art...")
                st.caption("⏳ High-quality generation may take 10-30 seconds...")
            else:
                st.markdown("🌌 **SmartBot Ludy 1.2** is visualizing your request...")
            
            try:
                # Use different generators based on model
                if st.session_state.selected_model == "genis_pro_70b":
                    img_bytes = generate_with_ludy_pro(prompt)
                    caption_text = "Created by SmartBot Ludy 2.0 Ultra (FLUX Pro 1.1 - Maximum Quality)"
                else:
                    img_bytes = generate_with_ludy_flash(prompt)
                    caption_text = "Created by SmartBot Ludy 1.2 (FLUX Schnell - Fast)"
                
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
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                actual_model = MODEL_MAP[st.session_state.selected_model]
                
                completion = client.chat.completions.create(
                    model=actual_model,
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🌌 Genis Control Hub")
    
    st.markdown("#### Select Your Model")
    model_choice = st.radio(
        "Choose processing power:",
        options=[
            "⚡ Genis Flash 1.2 (Fast & Efficient)",
            "🔥 Genis 2.0 Pro 70B (Maximum Power)"
        ],
        index=1 if st.session_state.selected_model == "genis_pro_70b" else 0
    )
    
    if "Flash 1.2" in model_choice:
        st.session_state.selected_model = "genis_flash_12"
        st.markdown("<div class='model-badge'>⚡ Genis Flash 1.2 Active</div>", unsafe_allow_html=True)
        st.info("**Current Features:**\n- ⚡ Lightning-fast text responses\n- 🎨 SmartBot Ludy 1.2 (FLUX Schnell)\n- 💨 Quick image generation")
    else:
        st.session_state.selected_model = "genis_pro_70b"
        st.markdown("<div class='pro-badge'>🔥 Genis 2.0 Pro 70B Active</div>", unsafe_allow_html=True)
        st.success("**Pro Features Unlocked:**\n- 🎨 SmartBot Ludy 2.0 Ultra (FLUX Pro 1.1)\n- 💎 Maximum quality images\n- 💡 Advanced reasoning\n- 🚀 70B processing power")
    
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
