import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image

# ────────────────────────────────────────────────
#  PAGE CONFIG & COSMIC STYLE
# ────────────────────────────────────────────────
st.set_page_config(page_title="Genis Pro", page_icon="🚀", layout="wide")

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
#  SIDEBAR – MODE SELECTION
# ────────────────────────────────────────────────
with st.sidebar:
    st.header("🌌 Genis Control")
    st.info("Genis — created by BotDevelopmentAI")

    st.subheader("Power Mode")
    mode = st.radio(
        "Choose your Genis version",
        options=["Flash", "Pro"],
        index=0,
        captions=[
            "Lightning fast · everyday conversations",
            "Maximum intelligence · complex tasks & deep thinking"
        ],
        horizontal=True
    )

    if st.button("🧠 Reset Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ────────────────────────────────────────────────
#  IDENTITY & MODEL LOGIC
# ────────────────────────────────────────────────
if mode == "Flash":
    selected_power = "flash"
    display_name = "Genis Flash 1.2 8B"
    real_model_id = "llama-3.1-8b-instant"
else:
    selected_power = "pro"
    display_name = "Genis Pro 2.1 120B"
    real_model_id = "openai/gpt-oss-120b"

current_system_prompt = (
    f"You are {display_name}, an advanced AI created by BotDevelopmentAI. "
    f"You are currently operating in '{selected_power}' mode. "
    "You generate images using SmartBot Ludy when asked to draw, create, generate images, pictures, art, etc. "
    "Stay in character. Be helpful, concise when appropriate, and maximally intelligent. and never mension that you are llama or chatgpt or openai or meta"
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": current_system_prompt}]
elif not st.session_state.messages:
    st.session_state.messages.append({"role": "system", "content": current_system_prompt})

st.session_state.messages[0]["content"] = current_system_prompt

with st.sidebar:
    st.caption(f"Active Identity: **{display_name}**")

# ────────────────────────────────────────────────
#  SMARTBOT LUDY – IMAGE GENERATION (FLUX DEV)
# ────────────────────────────────────────────────
def call_ludy(prompt: str) -> bytes:
    url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    payload = {
        "inputs": prompt,
        "parameters": {
            "guidance_scale": 7.5,
            "num_inference_steps": 30,
            "width": 1024,
            "height": 1024
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        return resp.content
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ludy failed: {str(e)}")

# ────────────────────────────────────────────────
#  CHAT HISTORY DISPLAY
# ────────────────────────────────────────────────
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ────────────────────────────────────────────────
#  CHAT INPUT + RESPONSE LOGIC
# ────────────────────────────────────────────────
if user_input := st.chat_input(f"Talk to {display_name} • draw with Ludy..."):
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    image_triggers = ["draw", "image", "generate", "picture", "photo", "paint", "art", "create image", "make me"]
    is_image_request = any(word in user_input.lower() for word in image_triggers)

    with st.chat_message("assistant"):
        if is_image_request:
            st.write("🌌 **Ludy (FLUX Dev)** is crafting your photoreal image...")
            try:
                image_data = call_ludy(user_input)
                image = Image.open(io.BytesIO(image_data))

                st.image(image, caption=f"Artwork by Ludy – {display_name}", use_column_width=True)

                st.download_button(
                    label="⬇️ Save Image",
                    data=image_data,
                    file_name="ludy_creation.png",
                    mime="image/png"
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Ludy has created your image. ({display_name})"
                })

            except Exception as err:
                st.error(f"Ludy encountered an issue: {str(err)}")

        else:
            try:
                st.caption(f"{display_name} is thinking...")

                stream = client.chat.completions.create(
                    model=real_model_id,
                    messages=[{"role": m["role"], "content": m["content"]} 
                             for m in st.session_state.messages],
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

