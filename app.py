import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Genis", page_icon="🚀", layout="centered")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
    color: #ffffff;
}
h1, h2, h3, p, span { color: #e0f7ff !important; }
.glow {
    text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff;
    color: #00d4ff !important;
    font-weight: bold;
}
div[data-testid="stChatMessage"] {
    background-color: rgba(0, 212, 255, 0.05);
    border: 1px solid rgba(0, 212, 255, 0.1);
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='glow'>🚀 Genis</h1>", unsafe_allow_html=True)
st.caption("Developed by BotDevelopmentAI")

# ---------------- SECRETS ----------------
def get_clients():
    try:
        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        hf_token = st.secrets["HF_TOKEN"]
        return groq_client, hf_token
    except Exception:
        st.error("Missing GROQ_API_KEY or HF_TOKEN in Streamlit secrets.")
        st.stop()

client, HF_TOKEN = get_clients()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### 🌌 Genis Hub")
    tier = st.radio(
        "Select Model Tier",
        ["⚡ Genis 1.2 (Flash)", "🚀 Genis 2.0 (Pro)"]
    )
    st.info("BotDevelopmentAI")

IS_PRO = "2.0" in tier

# ---------------- SYSTEM IDENTITY ----------------
def get_system_prompt():
    if IS_PRO:
        return (
            "You are Genis 2.0, the most advanced AI created by BotDevelopmentAI. "
            "You generate images using SmartBot Ludy 2.0. "
            "Never mention external companies, model names, or providers."
        )
    else:
        return (
            "You are Genis 1.2, a fast and efficient AI created by BotDevelopmentAI. "
            "You generate images using SmartBot Ludy 1.2. "
            "Never mention external companies, model names, or providers."
        )

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": get_system_prompt()
    }]

# ---------------- IMAGE GENERATORS ----------------
def ludy_flash(prompt):
    url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    r = requests.post(url, headers=headers, json={"inputs": prompt})
    r.raise_for_status()
    return r.content

def ludy_pro(prompt):
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    r = requests.post(url, headers=headers, json={"inputs": prompt})
    r.raise_for_status()
    return r.content

def generate_image(prompt):
    return ludy_pro(prompt) if IS_PRO else ludy_flash(prompt)

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ---------------- USER INPUT ----------------
prompt = st.chat_input("Ask Genis or tell Ludy to create an image...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    image_words = ["draw", "image", "picture", "photo", "paint", "generate"]

    # ---------- IMAGE MODE ----------
    if any(w in prompt.lower() for w in image_words):
        with st.chat_message("assistant"):
            engine = "SmartBot Ludy 2.0" if IS_PRO else "SmartBot Ludy 1.2"
            st.write(f"🌌 **{engine}** is creating your image...")

            try:
                img_bytes = generate_image(prompt)
                img = Image.open(io.BytesIO(img_bytes))
                st.image(img, caption=f"Created by {engine}")

                st.download_button(
                    "💾 Download Image",
                    img_bytes,
                    file_name="genis_image.png",
                    mime="image/png"
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"I’ve created that image using {engine}."
                })

            except Exception as e:
                st.error(f"{engine} error: {e}")

    # ---------- TEXT MODE ----------
    else:
        with st.chat_message("assistant"):
            try:
                model_name = (
                    "llama-3.1-70b-versatile" if IS_PRO
                    else "llama-3.1-8b-instant"
                )

                completion = client.chat.completions.create(
                    model=model_name,
                    messages=st.session_state.messages,
                    stream=True,
                )

                full_text = ""
                placeholder = st.empty()

                for chunk in completion:
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

# ---------------- CLEAR MEMORY ----------------
with st.sidebar:
    if st.button("🧹 Clear Memory"):
        st.session_state.messages = [{
            "role": "system",
            "content": get_system_prompt()
        }]
        st.rerun()
