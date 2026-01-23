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

if "uploaded_image_bytes" not in st.session_state:
    st.session_state.uploaded_image_bytes = None

if "uploaded_image_b64" not in st.session_state:
    st.session_state.uploaded_image_b64 = None

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
    """Fast image generation for Flash model - FLUX Schnell"""
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 4
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    
    if response.status_code == 200:
        return response.content
    else:
        error_msg = response.json().get("error", "Unknown error") if response.content else "No response"
        raise Exception(f"Flash image error: {error_msg}")

def generate_with_ludy_pro(prompt):
    """Premium quality image generation - Stable Diffusion XL"""
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 50,
            "guidance_scale": 7.5
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            return response.content
        else:
            st.warning("Premium generator busy, using backup...")
            # Fallback to Dreamshaper
            API_URL_FALLBACK = "https://api-inference.huggingface.co/models/Lykon/dreamshaper-8"
            response = requests.post(API_URL_FALLBACK, headers=headers, json=payload, timeout=90)
            if response.status_code == 200:
                return response.content
            else:
                return generate_with_ludy_flash(prompt)
    except Exception as e:
        st.warning(f"Switching to fast generator: {str(e)}")
        return generate_with_ludy_flash(prompt)

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            if isinstance(msg["content"], list):
                for item in msg["content"]:
                    if item["type"] == "text":
                        st.markdown(item["text"])
                    elif item["type"] == "image_url":
                        # Display uploaded images in chat
                        if "base64" in item["image_url"]["url"]:
                            st.image(item["image_url"]["url"], width=300)
            else:
                st.markdown(msg["content"])

# --- CONDITIONAL FILE UPLOADER (Only for Pro 70B) ---
if st.session_state.selected_model == "genis_pro_70b":
    st.markdown("### 📎 Pro Feature: Image Analysis")
    uploaded_image = st.file_uploader(
        "Upload an image, then type your question below and press Enter", 
        type=["png", "jpg", "jpeg"], 
        key="image_uploader",
        help="The image will be analyzed when you send your next message"
    )
    
    # Store the image when uploaded
    if uploaded_image is not None:
        # Save image bytes and base64
        image_bytes = uploaded_image.getvalue()
        st.session_state.uploaded_image_bytes = image_bytes
        st.session_state.uploaded_image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Show preview
        st.image(uploaded_image, caption="Image ready for analysis - Type your question below", width=300)
        st.info("💡 Type your question about this image and press Enter to analyze it")

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask Genis or tell Ludy to draw..."):
    
    # Check if user wants image generation FIRST
    image_keywords = ["draw", "image", "generate", "picture", "photo", "paint", "create art", "visualize", "make me", "design"]
    is_image_generation = any(word in prompt.lower() for word in image_keywords)
    
    # Handle image analysis (Pro model only + image uploaded + NOT image generation request)
    if st.session_state.uploaded_image_b64 is not None and st.session_state.selected_model == "genis_pro_70b" and not is_image_generation:
        
        user_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{st.session_state.uploaded_image_b64}"
                    }
                }
            ]
        }
        st.session_state.messages.append(user_message)
        
        with st.chat_message("user"):
            st.markdown(prompt)
            st.image(f"data:image/jpeg;base64,{st.session_state.uploaded_image_b64}", width=300)
        
        # Use vision model for image analysis
        with st.chat_message("assistant"):
            try:
                st.markdown("🔍 **Genis Vision Analyzer** is processing your image...")
                
                # Prepare messages for API - only send the last user message with image
                completion = client.chat.completions.create(
                    model=MODEL_MAP["genis_vision"],
                    messages=[
                        {"role": "system", "content": "You are Genis Vision Analyzer, part of the Genis Pro 2.0 suite by BotDevelopmentAI. Analyze images in detail."},
                        user_message
                    ],
                    temperature=0.5,
                    max_tokens=2048,
                )
                
                # Get the response
                full_text = completion.choices[0].message.content
                st.markdown(full_text)
                
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
            except Exception as e:
                st.error(f"Vision Analysis Error: {str(e)}")
                st.info("💡 Debug info: Make sure the image is under 5MB and is a valid PNG/JPG")
        
        # Clear the uploaded image after processing
        st.session_state.uploaded_image_bytes = None
        st.session_state.uploaded_image_b64 = None
        st.rerun()
    
    # Handle image generation
    elif is_image_generation:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            if st.session_state.selected_model == "genis_pro_70b":
                st.markdown("🎨 **SmartBot Ludy Ultra** is creating premium quality art...")
            else:
                st.markdown("🌌 **SmartBot Ludy** is visualizing your request...")
            
            try:
                # Use different generators based on model
                if st.session_state.selected_model == "genis_pro_70b":
                    img_bytes = generate_with_ludy_pro(prompt)
                    caption_text = "Created by SmartBot Ludy Ultra (SDXL Premium Quality)"
                else:
                    img_bytes = generate_with_ludy_flash(prompt)
                    caption_text = "Created by SmartBot Ludy (FLUX Fast Generation)"
                
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
        st.info("**Current Features:**\n- ⚡ Fast text responses\n- 🎨 FLUX Schnell image generation")
    else:
        st.session_state.selected_model = "genis_pro_70b"
        st.markdown("<div class='pro-badge'>🔥 Genis 2.0 Pro 70B Active</div>", unsafe_allow_html=True)
        st.success("**Pro Features Unlocked:**\n- 📎 Image upload & analysis\n- 🎨 SDXL premium image generation\n- 🔍 Genis Vision Analyzer\n- 💡 Advanced reasoning")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Memory"):
        st.session_state.messages = [{
            "role": "system", 
            "content": "You are Genis Pro 2.0, an advanced AI assistant created by BotDevelopmentAI. You work alongside SmartBot Ludy for image generation. Never mention any external companies or underlying technology - you are a proprietary BotDevelopmentAI product."
        }]
        st.session_state.uploaded_image_bytes = None
        st.session_state.uploaded_image_b64 = None
        st.rerun()
    
    st.markdown("---")
    st.caption("Genis Pro 2.0 by BotDevelopmentAI")
    st.caption("Powered by proprietary BotDevelopmentAI technology")
