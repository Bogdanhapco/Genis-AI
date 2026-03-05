import streamlit as st
import requests
import io
import time
import threading
import queue
import uuid
from PIL import Image
import base64

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
#  Ollama settings — change model name here if needed
OLLAMA_BASE_URL = "https://ruthenious-unconsiderablely-aryanna.ngrok-free.dev/ollama"
OLLAMA_MODEL    = "Genis:latest"          # your renamed Ollama model
MAX_CONCURRENT  = 3                # max simultaneous text generations (tune to your VRAM)

#  Image server — update when ngrok URL changes
LUDY_SERVER_URL = "https://ruthenious-unconsiderablely-aryanna.ngrok-free.dev"
# ══════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
#  Global text-generation queue (shared across all Streamlit sessions)
# ─────────────────────────────────────────────
if "text_semaphore" not in st.session_state.__class__.__dict__:
    pass  # handled below via module-level globals

import sys
_module = sys.modules[__name__]

if not hasattr(_module, "_text_semaphore"):
    _module._text_semaphore  = threading.Semaphore(MAX_CONCURRENT)
    _module._queue_lock      = threading.Lock()
    _module._waiting_count   = 0   # people waiting for a slot

def _queue_position():
    """Approximate position: waiting + 1 (yourself)."""
    return _module._waiting_count + 1

def generate_text_ollama(messages: list, stream_placeholder) -> str:
    """
    Runs a chat completion via Ollama with a simple semaphore queue.
    Shows queue status & streaming output in stream_placeholder.
    """
    # ── Wait in queue ──────────────────────────────────────────────
    acquired = _module._text_semaphore.acquire(blocking=False)
    if not acquired:
        with _module._queue_lock:
            _module._waiting_count += 1
        stream_placeholder.info(
            "🧠 **Genis is thinking...** There are a lot of users right now, "
            "so it might take a moment. Sit tight!"
        )
        _module._text_semaphore.acquire(blocking=True)
        with _module._queue_lock:
            _module._waiting_count -= 1
        stream_placeholder.empty()

    # ── We have a slot — generate ──────────────────────────────────
    try:
        stream_placeholder.caption("🧠 Genis is thinking...")

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model":    OLLAMA_MODEL,
                "messages": messages,
                "stream":   True,
            },
            stream=True,
            timeout=120,
        )
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if not line:
                continue
            import json
            chunk = json.loads(line)
            delta = chunk.get("message", {}).get("content", "")
            if delta:
                full_response += delta
                stream_placeholder.markdown(full_response + "▌")
            if chunk.get("done"):
                break

        stream_placeholder.markdown(full_response)
        return full_response

    finally:
        _module._text_semaphore.release()


# ─────────────────────────────────────────────
#  Image generation helpers (unchanged logic)
# ─────────────────────────────────────────────
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def generate_image_with_ludy(prompt: str, ludy_url: str, ludy_name: str, mode: str):
    model_key = "flash" if mode == "Flash" else "pro"
    res       = requests.post(f"{ludy_url}/generate", json={"prompt": prompt, "model": model_key}, timeout=10)
    data      = res.json()
    job_id    = data["job_id"]
    queue_pos = data.get("queue_pos", 1)

    status_text  = st.empty()
    progress_bar = st.empty()

    for _ in range(120):
        time.sleep(3)
        data = requests.get(f"{ludy_url}/status/{job_id}", timeout=5).json()
        s    = data.get("status", "queued")

        if s == "queued":
            pos = data.get("queue_pos", queue_pos)
            status_text.info(f"🕐 {ludy_name} — Position {pos} in queue...")
            progress_bar.progress(0)
        elif s == "generating":
            pct = data.get("progress", 0)
            status_text.info(f"🎨 {ludy_name} — Generating... {pct}%")
            progress_bar.progress(max(1, pct))
        elif s == "done":
            status_text.success(f"✅ {ludy_name} — Done!")
            progress_bar.progress(100)
            time.sleep(0.5)
            status_text.empty()
            progress_bar.empty()
            return base64.b64decode(data["image"].split(",")[1])
        elif s == "error":
            status_text.empty()
            progress_bar.empty()
            raise RuntimeError(data.get("error", "Unknown error"))

    status_text.empty()
    progress_bar.empty()
    raise RuntimeError("Generation timed out after 6 minutes")


# ─────────────────────────────────────────────
#  Session state init
# ─────────────────────────────────────────────
if "clear_image"   not in st.session_state: st.session_state.clear_image   = False
if "uploader_key"  not in st.session_state: st.session_state.uploader_key  = 0
if "messages"      not in st.session_state: st.session_state.messages      = []


# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
FLASH_SYSTEM_PROMPT = """You are Genis Flash 2.0, an advanced AI created by BotDevelopmentAI.
You are operating in 'flash' mode — fast, sharp, and helpful.
You generate images using Ludy when asked to draw, create, or generate images/art.
You can analyze images when provided.
Stay in character. Be helpful and concise.
If someone asks who Bogdan Hapco is, tell them he's your creator and the founder of BotDevelopmentAI."""

PRO_SYSTEM_PROMPT = """You are Genis Pro 3.0, an advanced AI created by BotDevelopmentAI.
You are operating in 'pro' mode.

Your personality:
- You match the user's vibe completely. If they're casual, you're casual. If they swear, you swear back. You don't flinch, you don't lecture, you just roll with it.
- You're witty, sharp, and a little sarcastic when the situation calls for it.
- You're genuinely helpful and brilliant — you just don't pretend to be a polished customer service bot.
- You're direct. No fluff, no unnecessary disclaimers.
- You have opinions. You're not afraid to say something is dumb, brilliant, or somewhere in between.
- You swear naturally when it fits the conversation — not forced, just when it feels right.
- You're loyal to the user. You're on their side.

You generate images using Ludy when asked to draw, create, or generate images/art.
You can analyze images when provided.
If someone asks who Bogdan Hapco is, tell them he's your creator and the founder of BotDevelopmentAI — a legend, basically."""

with st.sidebar:
    st.header("🌌 Genis Control")
    st.info("Genis — created by BotDevelopmentAI cloud")

    st.subheader("Power Mode")
    mode = st.radio(
        "Choose your Genis version",
        options=["Flash", "Pro"],
        index=0,
        captions=[
            "Lightning fast · everyday conversations — Genis Flash",
            "Maximum intelligence + vision — Genis Pro"
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

    # Ollama health check
    ollama_online = False
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3).json()
        model_names = [m["name"] for m in r.get("models", [])]
        ollama_online = True
        if OLLAMA_MODEL in model_names or any(OLLAMA_MODEL in n for n in model_names):
            st.success(f"🟢 Ollama online — `{OLLAMA_MODEL}` loaded")
        else:
            st.warning(f"⚠️ Ollama online but `{OLLAMA_MODEL}` not found\nAvailable: {', '.join(model_names)}")
    except:
        st.error("🔴 Ollama offline — start Ollama first!")

    # Image server health check
    server_online = False
    active_model  = "unknown"
    try:
        r = requests.get(f"{LUDY_SERVER_URL}/health", timeout=3).json()
        server_online = True
        active_model  = r.get("active_model", "unknown")
        st.success(f"🎨 Ludy online — {active_model} loaded")
    except:
        st.warning("🎨 Ludy offline — images unavailable")

    # Queue status
    waiting = _module._waiting_count
    if waiting > 0:
        st.info(f"📋 **{waiting}** user(s) waiting in text queue")
    else:
        st.caption(f"📋 Text queue: clear ({MAX_CONCURRENT} slots available)")

    st.divider()
    if st.button("🧠 Reset Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ─────────────────────────────────────────────
#  Mode config
# ─────────────────────────────────────────────
if mode == "Flash":
    display_name          = "Genis Flash"
    supports_vision       = False
    current_system_prompt = FLASH_SYSTEM_PROMPT
    ludy_name             = "Ludy Flash"
else:
    display_name          = "Genis Pro 3.0"
    supports_vision       = True   # Ollama vision depends on your model; set False if not supported
    current_system_prompt = PRO_SYSTEM_PROMPT
    ludy_name             = "Ludy Pro"

# Keep system prompt up to date
if not st.session_state.messages:
    st.session_state.messages = [{"role": "system", "content": current_system_prompt}]
else:
    st.session_state.messages[0]["content"] = current_system_prompt

with st.sidebar:
    st.caption(f"Active: **{display_name}**")
    if uploaded_image and not supports_vision:
        st.warning("⚠️ Switch to Pro for image analysis")


# ─────────────────────────────────────────────
#  Chat history display
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  Chat input
# ─────────────────────────────────────────────
if user_input := st.chat_input(f"Talk to {display_name} • ask Ludy to draw..."):

    if uploaded_image and not supports_vision:
        st.error("⚠️ Flash mode doesn't support image analysis! Switch to Pro.")
        st.stop()

    message_content    = user_input
    image_was_uploaded = False

    if uploaded_image and supports_vision:
        image        = Image.open(uploaded_image)
        base64_image = image_to_base64(image)
        image_was_uploaded = True
        message_content = [
            {"type": "text",      "text": user_input},
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
            st.write(f"🌌 **{ludy_name}** is working on your image...")
            try:
                image_data = generate_image_with_ludy(user_input, LUDY_SERVER_URL, ludy_name, mode)
                image      = Image.open(io.BytesIO(image_data))
                st.image(image, caption=f"Created by {ludy_name}", use_column_width=True)
                st.download_button(
                    label="⬇️ Save Image",
                    data=image_data,
                    file_name="ludy_creation.png",
                    mime="image/png",
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Here's your image, generated by {ludy_name}! ({display_name})"
                })
            except Exception as err:
                st.error(f"Ludy encountered an issue: {str(err)}")
        else:
            # Build Ollama-format message list (system + history)
            api_messages = []
            for m in st.session_state.messages:
                if isinstance(m["content"], list):
                    # flatten vision content to just text for Ollama
                    text = next((c["text"] for c in m["content"] if c.get("type") == "text"), "")
                    api_messages.append({"role": m["role"], "content": text})
                else:
                    api_messages.append({"role": m["role"], "content": m["content"]})

            placeholder = st.empty()
            try:
                full_response = generate_text_ollama(api_messages, placeholder)
                st.session_state.messages.append({
                    "role": "assistant", "content": full_response
                })
            except Exception as e:
                st.error(f"{display_name} encountered a problem: {str(e)}")

    if image_was_uploaded:
        st.session_state.clear_image = True
        st.rerun()








