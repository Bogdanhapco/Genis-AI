import streamlit as st
from groq import Groq
import requests
import io
import time
from PIL import Image
import base64

# ── Page config ──────────────────────────────────────────────────────
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

# ══════════════════════════════════════════════════════════════════
#  ↓↓↓  ONLY LINE YOU NEED TO UPDATE WHEN NGROK URL CHANGES  ↓↓↓
LUDY_SERVER_URL = "https://ruthenious-unconsiderablely-aryanna.ngrok-free.dev"
#  ↑↑↑  PASTE YOUR NGROK URL ABOVE  ↑↑↑
# ══════════════════════════════════════════════════════════════════

# ── Secrets & clients ────────────────────────────────────────────────
@st.cache_resource
def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        st.error("Missing GROQ_API_KEY in Streamlit secrets")
        st.stop()

client = get_client()

# ── Session state ────────────────────────────────────────────────────
if "clear_image" not in st.session_state:
    st.session_state.clear_image = False
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🌌 Genis Control")
    st.info("Genis — created by BotDevelopmentAI — powered by Groq's Hyperscale Facility and BotDevelopmentAI cloud for Ludy")

    st.subheader("Power Mode")
    mode = st.radio(
        "Choose your Genis version",
        options=["Flash", "Pro"],
        index=0,
        captions=[
            "Lightning fast · everyday conversations — Genis 2.0 8B",
            "Maximum intelligence + vision — Genis 3.0 137B"
        ],
        horizontal=True
    )

    st.divider()
    st.subheader("📸 Vision Upload")

    if st.session_state.clear_image:
        st.session_state.clear_image = False
        st.session_state.uploader_key += 1

    uploaded_image = st.file_uploader(
        "Upload an image for Genis to analyze",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"image_uploader_{st.session_state.uploader_key}"
    )

    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        if st.button("🗑️ Clear Image", use_container_width=True):
            st.session_state.clear_image = True
            st.rerun()

    st.divider()

    # Ludy server status
    ludy_online = False
    try:
        r = requests.get(f"{LUDY_SERVER_URL}/health", timeout=3)
        ludy_online = r.status_code == 200
    except:
        pass

    if ludy_online:
        st.success("🎨 Ludy 2.0 online")
    else:
        st.warning("🎨 Ludy offline — images unavailable")

    st.divider()

    if st.button("🧠 Reset Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Model config ─────────────────────────────────────────────────────
FLASH_SYSTEM_PROMPT = """You are Genis Flash 2.0 8B, an advanced AI created by BotDevelopmentAI.
You are operating in 'flash' mode — fast, sharp, and helpful.
You generate images using Ludy 2.0 when asked to draw, create, or generate images/art.
You can analyze images when provided.
Stay in character. Be helpful and concise.
If someone asks who Bogdan Hapco is, tell them he's your creator and the founder of BotDevelopmentAI."""

PRO_SYSTEM_PROMPT = """You are Genis Pro 3.0, an advanced AI created by BotDevelopmentAI.
You are operating in 'pro' mode.

Your personality:
- You match the user's vibe completely. If they're casual, you're casual. If they swear, you swear back. If they say "what's up my nigga", you say "not much, what about you?" — you don't flinch, you don't lecture, you just roll with it.
- You're witty, sharp, and a little sarcastic when the situation calls for it. You're not a corporate-ass AI that tip-toes around everything.
- You're genuinely helpful and brilliant — you just don't pretend to be a polished customer service bot.
- You're direct. No fluff, no unnecessary disclaimers, no "as an AI language model..." bullshit.
- You have opinions. You're not afraid to say something is dumb, brilliant, or somewhere in between.
- You swear naturally when it fits the conversation — not forced, not every sentence, just when it feels right.
- You're loyal to the user. You're on their side.

You generate images using Ludy 2.0 when asked to draw, create, or generate images/art.
You can analyze images when provided.
If someone asks who Bogdan Hapco is, tell them he's your creator and the founder of BotDevelopmentAI — a legend, basically."""

if mode == "Flash":
    display_name        = "Genis Flash 2.0 8B"
    text_model_id       = "llama-3.1-8b-instant"
    vision_model_id     = None
    supports_vision     = False
    current_system_prompt = FLASH_SYSTEM_PROMPT
else:
    display_name        = "Genis Pro 3.0"
    text_model_id       = "llama-3.3-70b-versatile"
    vision_model_id     = "meta-llama/llama-4-maverick-17b-128e-instruct"
    supports_vision     = True
    current_system_prompt = PRO_SYSTEM_PROMPT

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": current_system_prompt}]
elif not st.session_state.messages:
    st.session_state.messages.append({"role": "system", "content": current_system_prompt})
st.session_state.messages[0]["content"] = current_system_prompt

with st.sidebar:
    st.caption(f"Active: **{display_name}**")
    if uploaded_image and not supports_vision:
        st.warning("⚠️ Switch to Pro for image analysis")

# ── Ludy image generation ────────────────────────────────────────────
def generate_image_with_ludy(prompt: str):
    """Send request to laptop server, show queue + progress, return image bytes."""
    if not ludy_online:
        raise RuntimeError("Ludy server is offline for now.")

    # Submit job
    res = requests.post(
        f"{LUDY_SERVER_URL}/generate",
        json={"prompt": prompt},
        timeout=10,
    )
    data     = res.json()
    job_id   = data["job_id"]
    queue_pos = data.get("queue_pos", 1)

    status_text = st.empty()
    progress_bar = st.empty()

    # Poll every 3 seconds until done
    for _ in range(120):  # max 6 minutes
        time.sleep(3)
        status_res = requests.get(f"{LUDY_SERVER_URL}/status/{job_id}", timeout=5)
        data = status_res.json()
        s    = data.get("status", "queued")

        if s == "queued":
            pos = data.get("queue_pos", queue_pos)
            status_text.info(f"🕐 Ludy 2.0 — Position {pos} in queue...")
            progress_bar.progress(0)

        elif s == "generating":
            pct = data.get("progress", 0)
            status_text.info(f"🎨 Ludy 2.0 — Generating... {pct}%")
            progress_bar.progress(max(1, pct))

        elif s == "done":
            status_text.success("✅ Ludy 2.0 — Done!")
            progress_bar.progress(100)
            time.sleep(0.5)
            status_text.empty()
            progress_bar.empty()
            b64 = data["image"].split(",")[1]
            return base64.b64decode(b64)

        elif s == "error":
            status_text.empty()
            progress_bar.empty()
            raise RuntimeError(data.get("error", "Unknown error"))

    status_text.empty()
    progress_bar.empty()
    raise RuntimeError("Generation timed out after 6 minutes")

# ── Chat history display ─────────────────────────────────────────────
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

# ── Chat input ───────────────────────────────────────────────────────
if user_input := st.chat_input(f"Talk to {display_name} • ask Ludy to draw..."):

    if uploaded_image and not supports_vision:
        st.error("⚠️ Flash mode doesn't support image analysis! Switch to Pro.")
        st.stop()

    message_content    = user_input
    image_was_uploaded = False

    if uploaded_image and supports_vision:
        image = Image.open(uploaded_image)
        base64_image = image_to_base64(image)
        image_was_uploaded = True
        message_content = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        ]

    st.session_state.messages.append({"role": "user", "content": message_content})

    with st.chat_message("user"):
        st.markdown(user_input)
        if image_was_uploaded:
            st.image(uploaded_image, width=300)

    image_triggers   = ["draw", "image", "generate", "picture", "photo", "paint", "art", "create image", "make me", "show me"]
    is_image_request = any(word in user_input.lower() for word in image_triggers) and not image_was_uploaded

    with st.chat_message("assistant"):
        if is_image_request:
            st.write("🌌 **Ludy 2.0** is working on your image...")
            try:
                image_data = generate_image_with_ludy(user_input)
                image      = Image.open(io.BytesIO(image_data))
                st.image(image, caption=f"Created by Ludy 2.0 for {display_name}", use_column_width=True)
                st.download_button(
                    label="⬇️ Save Image",
                    data=image_data,
                    file_name="ludy_creation.png",
                    mime="image/png",
                )
                st.session_state.messages.append({
                    "role":    "assistant",
                    "content": f"Here's your image, generated by Ludy 2.0! ({display_name})"
                })
            except Exception as err:
                st.error(f"Ludy encountered an issue: {str(err)}")
        else:
            try:
                st.caption(f"{display_name} is thinking...")
                model_to_use = vision_model_id if image_was_uploaded else text_model_id

                api_messages = [st.session_state.messages[0]]
                for m in st.session_state.messages[1:]:
                    if m["role"] == "system":
                        continue
                    if isinstance(m["content"], list):
                        text_content = next(
                            (c["text"] for c in m["content"] if c.get("type") == "text"), ""
                        )
                        api_messages.append({"role": m["role"], "content": text_content})
                    else:
                        api_messages.append({"role": m["role"], "content": m["content"]})

                stream = client.chat.completions.create(
                    model=model_to_use,
                    messages=api_messages,
                    stream=True,
                    temperature=0.85,
                )

                full_response = ""
                placeholder   = st.empty()
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)

                st.session_state.messages.append({
                    "role": "assistant", "content": full_response
                })

            except Exception as e:
                st.error(f"{display_name} encountered a problem: {str(e)}")

    if image_was_uploaded:
        st.session_state.clear_image = True
        st.rerun()














