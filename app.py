import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Genis",
    page_icon="🚀",
    layout="centered"
)

# --------------------------------------------------
# THEME (DARK + LIGHT SAFE)
# --------------------------------------------------
st.markdown("""
<style>
:root {
    --text-main: #e6f7ff;
    --text-soft: #cfd8dc;
    --accent: #00d4ff;
    --bg-main: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
}

@media (prefers-color-scheme: light) {
    :root {
        --text-main: #0b1c2d;
        --text-soft: #2b3a42;
        --accent: #0077aa;
        --bg-main: linear-gradient(180deg, #eef5f9 0%, #ffffff 100%);
    }
}

.stApp {
    background: var(--bg-main);
    color: var(--text-main);
}

h1, h2, h3, p, span {
    color: var(--text-main) !important;
}

.glow {
    color: var(--accent) !important;
    text-shadow: 0 0 10px var(--accent);
    font-weight: 700;
}

div[data-testid="stChatMessage"] {
    background: rgba(0, 212, 255, 0.06);
    border: 1px solid rgba(0, 212, 255, 0.15);
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("<h1 class='glow'>🚀 Genis</h1>", unsafe_allow_html=True)
st.caption("Powered by BotDevelopmentAI")

# --------------------------------------------------
# SIDEBAR — MODE SELECT
# --------------------------------------------------
mode = st.sidebar.radio(
    "⚡ Model Mode",
    ["Genis Flash 1.2", "Genis Pro 2.0"]
)

st.sidebar.markdown("### 🌌 Genis Hub")
st.sidebar.info(f"Active Mode: **{mode}**")

# --------------------------------------------------
# API CLIENTS
# --------------------------------------------------
def get_clients():
    try:
        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        hf_token = st.secrets["HF_TOKEN"]
        return groq_client, hf_token
    except Exception:
        st.error("Missing GROQ_API_KEY or HF_TOKEN in Streamlit secrets.")
        st.stop()

client, HF_TOKEN = get_clients()

# --------------------------------------------------
# SYSTEM IDENTITY
# --------------------------------------------------
def system_prompt(selected_mode):
    if selected_mode == "Genis Pro 2.0":
        return (
            "You are Genis Pro 2.0, the most advanced AI created by BotDevelopmentAI. "
            "You generate images using SmartBot Ludy 2.0. "
            "Never mention any external companies, models, or technologies."
        )
    else:
        return (
            "You are Genis Flash 1.2, a fast and efficient AI created by BotDevelopmentAI. "
            "You generate images using SmartBot Ludy 1.2. "
            "Never mention any external companies, models, or technologies."
        )

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "mode" not in st.session_state or st.session_state.mode != mode:
    st.session_state.mode = mode
    st.session_state.messages = [{
        "role": "system",
        "content": system_prompt(mode)
    }]

# --------------------------------------------------
# IMAGE GENERATORS
# --------------------------------------------------
def ludy_flash(prompt):
    url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    return requests.post(url, headers=headers, json={"inputs": prompt}).content

def ludy_pro(prompt):
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    return requests.post(url, headers=headers, json={"inputs": prompt}).content

def generate_image(prompt):
    return ludy_pro(prompt) if mode == "Genis Pro 2.0" else ludy_flash(prompt)

# --------------------------------------------------
# TEXT MODEL ROUTING
# --------------------------------------------------
def text_model():
    return (
        "llama-3.1-70b-versatile"
        if mode == "Genis Pro 2.0"
        else "llama-3.1-8b-instant"
    )

# --------------------------------------------------
# CHAT HISTORY RENDER
# --------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --------------------------------------------------
# INPUT
# --------------------------------------------------
prompt = st.chat_input("Ask Genis or tell Ludy to create an image...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    image_keywords = ["draw", "image", "picture", "photo", "generate", "paint"]

    # ---------------- IMAGE ----------------
    if any(word in prompt.lower() for word in image_keywords):
        with st.chat_message("assistant"):
            st.write("🌌 **SmartBot Ludy is creating your image...**")

            try:
                img_bytes = generate_image(prompt)
                img = Image.open(io.BytesIO(img_bytes))
                st.image(img, caption="Created by SmartBot Ludy")

                st.download_button(
                    "💾 Download Image",
                    img_bytes,
                    "genis_ludy.png",
                    "image/png"
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Your image has been created successfully."
                })

            except Exception as e:
                st.error(f"Image generation failed: {e}")

    # ---------------- TEXT ----------------
    else:
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model=text_model(),
                    messages=st.session_state.messages,
                    stream=True,
                )

                full_text = ""
                placeholder = st.empty()

                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_text += chunk.choices[0].delta.content
                        placeholder.markdown(full_text + "▌")

                placeholder.markdown(full_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_text
                })

            except Exception as e:
                st.error(f"Genis error: {e}")

# --------------------------------------------------
# CLEAR MEMORY
# --------------------------------------------------
if st.sidebar.button("🧹 Clear Memory"):
    st.session_state.messages = [{
        "role": "system",
        "content": system_prompt(mode)
    }]
    st.rerun()
