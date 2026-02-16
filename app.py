import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image
import base64

# ────────────────────────────────────────────────
#  PAGE CONFIG & COSMIC STYLE
# ────────────────────────────────────────────────
st.set_page_config(page_title="Genis Pro", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(ellipse at bottom, #0f172a 0%, #02040f 100%);
        color: #e0f7ff;
    }
    h1, h2, h3, .stMarkdown, p, span, div { color: #e0f7ff !important; }
    .glow { 
        text-shadow: 0 0 15px #00d4ff, 0 0 30px #00d4ff; 
        color: #00f0ff !important; 
        font-weight: bold; 
    }
    div[data-testid="stChatMessage"] {
        background: rgba(0, 212, 255, 0.06);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 16px;
        padding: 12px 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='glow'>🚀 Genis</h1>", unsafe_allow_html=True)
st.caption("by BotDevelopmentAI")

# ────────────────────────────────────────────────
#  SECRETS & CLIENTS
# ────────────────────────────────────────────────
@st.cache_resource
def get_clients():
    try:
        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        hf_token = st.secrets["HF_TOKEN"]
        return groq_client, hf_token
    except Exception:
        st.error("Missing API keys in Streamlit secrets (GROQ_API_KEY + HF_TOKEN)")
        st.stop()

client, HF_TOKEN = get_clients()

# ────────────────────────────────────────────────
#  SESSION STATE INITIALIZATION
# ────────────────────────────────────────────────
if "clear_image" not in st.session_state:
    st.session_state.clear_image = False
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# ────────────────────────────────────────────────
#  HELPER: Convert Image to Base64
# ────────────────────────────────────────────────
def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# ────────────────────────────────────────────────
#  SIDEBAR – MODE SELECTION & IMAGE UPLOAD
# ────────────────────────────────────────────────
with st.sidebar:
    st.header("🌌 Genis Control")
    st.info("Genis — created by BotDevelopmentAI")

    st.subheader("Power Mode")
    mode = st.radio(
        "Choose your Genis version",
        options=["Flash", "Pro"],
        index=0,  # Flash is now default
        captions=[
            "Lightning fast · everyday conversations",
            "Maximum intelligence · complex tasks & deep thinking"
        ],
        horizontal=True
    )

    st.divider()
    
    # Image Upload Section
    st.subheader("📸 Vision Upload")
    
    # Clear the uploader if flag is set
    if st.session_state.clear_image:
        st.session_state.clear_image = False
        st.session_state.uploader_key += 1  # Change key to reset uploader
    
    uploaded_image = st.file_uploader(
        "Upload an image for Genis to analyze",
        type=["png", "jpg", "jpeg", "webp"],
        help="Upload an image and ask questions about it",
        key=f"image_uploader_{st.session_state.uploader_key}"
    )
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        if st.button("🗑️ Clear Image", use_container_width=True):
            st.session_state.clear_image = True
            st.rerun()
    
    st.divider()

    if st.button("🧠 Reset Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ────────────────────────────────────────────────
#  IDENTITY & MODEL LOGIC
# ────────────────────────────────────────────────

if mode == "Flash":
    selected_power = "flash"
    display_name = "Genis Flash 2.0 8B"
    real_model_id = "llama-3.1-8b-instant"  # Llama 3.1 8B Instant
    vision_model_id = None
    supports_vision = False
else:
    selected_power = "pro"
    display_name = "Genis Pro 2.2 137B"
    real_model_id = "openai/gpt-oss-120b"  # Keep the big 120B model for text!
    vision_model_id = "meta-llama/llama-4-maverick-17b-128e-instruct"  # Use Maverick only for vision
    supports_vision = True

current_system_prompt = (
    f"You are {display_name}, an advanced AI created by BotDevelopmentAI. "
    f"You are currently operating in '{selected_power}' mode. "
    "You generate images using SmartBot Ludy when asked to draw, create, generate images, pictures, art, etc. "
    "You can also analyze images when they are provided to you. "
    "Stay in character. Be helpful, concise when appropriate, and maximally intelligent. "
    "If someone asks you Who is Bogdan Hapco, you have to respond that he is the creator of you and he is the founder of BotDevelopmentAI"
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": current_system_prompt}]
elif not st.session_state.messages:
    st.session_state.messages.append({"role": "system", "content": current_system_prompt})

st.session_state.messages[0]["content"] = current_system_prompt

with st.sidebar:
    st.caption(f"Active Identity: **{display_name}**")
    if uploaded_image and not supports_vision:
        st.warning("⚠️ Switch to Pro mode for image analysis")

# ────────────────────────────────────────────────
#  SMARTBOT LUDY – IMAGE GENERATION
# ────────────────────────────────────────────────
def call_ludy(prompt: str) -> bytes:
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        resp = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=45)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        error_text = e.response.json().get("error", "no details") if hasattr(e, "response") else str(e)
        raise RuntimeError(f"SmartBot Ludy failed: {error_text}")

# ────────────────────────────────────────────────
#  CHAT HISTORY DISPLAY
# ────────────────────────────────────────────────
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if isinstance(message["content"], list):
                for content in message["content"]:
                    if content.get("type") == "text":
                        st.markdown(content["text"])
                    elif content.get("type") == "image_url":
                        st.info("🖼️ Image was included in this message")
            else:
                st.markdown(message["content"])

# ────────────────────────────────────────────────
#  CHAT INPUT + RESPONSE LOGIC
# ────────────────────────────────────────────────
if user_input := st.chat_input(f"Talk to {display_name} • draw with Ludy..."):
    
    # Check if user is trying to send an image with Flash model
    if uploaded_image and not supports_vision:
        st.error("⚠️ **Flash mode doesn't support image analysis!** Please switch to **Pro mode** in the sidebar to analyze images.")
        st.stop()
    
    message_content = user_input
    image_was_uploaded = False
    
    # If image is uploaded and Pro mode is active, include it
    if uploaded_image and supports_vision:
        image = Image.open(uploaded_image)
        base64_image = image_to_base64(image)
        image_was_uploaded = True
        
        message_content = [
            {
                "type": "text",
                "text": user_input
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            }
        ]
    
    st.session_state.messages.append({"role": "user", "content": message_content})
    
    # Add system prompt reinforcement after user message to maintain identity
    system_reinforcement = (
        f"Remember: You are {display_name}, created by BotDevelopmentAI. "
        f"You are in '{selected_power}' mode. Stay in character."
    )
    st.session_state.messages.append({"role": "system", "content": system_reinforcement})
    
    with st.chat_message("user"):
        st.markdown(user_input)
        if image_was_uploaded:
            st.image(uploaded_image, width=300)

    image_triggers = ["draw", "image", "generate", "picture", "photo", "paint", "art", "create image", "make me"]
    is_image_request = any(word in user_input.lower() for word in image_triggers) and not image_was_uploaded

    with st.chat_message("assistant"):
        if is_image_request:
            st.write(f"🌌 **Ludy 1.2** is channeling your vision...")
            try:
                image_data = call_ludy(user_input)
                image = Image.open(io.BytesIO(image_data))
                
                st.image(image, caption=f"Artwork by Ludy 1.2 – {display_name}", use_column_width=True)
                
                st.download_button(
                    label="⬇️ Save Image",
                    data=image_data,
                    file_name="ludy_creation.png",
                    mime="image/png",
                    use_container_width=False
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Ludy 1.2 has created your image. ({display_name})"
                })
            except Exception as err:
                st.error(f"Ludy encountered an issue: {str(err)}")
        
        else:
            try:
                st.caption(f"{display_name} is thinking...")
                
                # Choose model based on whether image is present in CURRENT message
                current_has_image = uploaded_image and supports_vision
                if current_has_image:
                    # Use vision model when image is uploaded
                    model_to_use = vision_model_id
                else:
                    # Use main model (GPT-OSS 120B) for text-only
                    model_to_use = real_model_id
                
                # Prepare messages for API call
                api_messages = []
                for m in st.session_state.messages:
                    # Convert multimodal messages to text-only for GPT-OSS 120B
                    if isinstance(m["content"], list) and not current_has_image:
                        # Extract just the text from multimodal messages
                        text_content = ""
                        for content in m["content"]:
                            if content.get("type") == "text":
                                text_content = content["text"]
                                break
                        api_messages.append({"role": m["role"], "content": text_content})
                    else:
                        # Keep as-is for vision model or text-only messages
                        api_messages.append({"role": m["role"], "content": m["content"]})
                
                stream = client.chat.completions.create(
                    model=model_to_use,
                    messages=api_messages,
                    stream=True,
                    temperature=0.7,
                )

                full_response = ""
                placeholder = st.empty()

                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response
                })

            except Exception as e:
                st.error(f"{display_name} encountered a problem: {str(e)}")
    
    # Auto-clear image after message is sent and processed
    if image_was_uploaded:
        st.session_state.clear_image = True
        st.rerun()
