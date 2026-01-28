import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image

# --- THEME & SPACE BACKGROUND ---
st.set_page_config(page_title="Genis Pro 1.2", page_icon="🚀")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
        color: #ffffff;
    }
    h1, h2, h3, p, span { color: #e0f7ff !important; }
    .glow { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; color: #00d4ff !important; font-weight: bold; }
    div[data-testid="stChatMessage"] { 
        background-color: rgba(0, 212, 255, 0.05); 
        border: 1px solid rgba(0, 212, 255, 0.1); 
        border-radius: 15px; 
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='glow'>🚀 Genis Pro 1.2</h1>", unsafe_allow_html=True)
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

# --- MODEL SELECTION (NEW) ---
with st.sidebar:
    st.markdown("### 🌌 Genis Hub")
    st.info("Genis Pro 1.2 by BotDevelopmentAI")
    
    st.markdown("### Mode / Model")
    model_choice = st.radio(
        "Select Genis mode:",
        options=["Flash (fast 8B)", "Pro (powerful 70B)"],
        index=0,  # default Flash
        help="Flash = speed, Pro = smarter & more capable answers"
    )
    
    if model_choice == "Flash (fast 8B)":
        selected_model = "llama-3.1-8b-instant"
        model_label = "Genis Flash"
    else:
        selected_model = "llama-3.1-70b-versatile"   # or try "llama-3.3-70b-versatile"
        model_label = "Genis Pro"
    
    st.caption(f"Using: **{model_label}** ({selected_model})")
    
    if st.button("Clear Memory"):
        if "messages" in st.session_state:
            st.session_state.messages = st.session_state.messages[:1]
        st.rerun()

# --- BRAINWASHING & IDENTITY ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": (
            f"You are {model_label} 1.2, made by BotDevelopmentAI. "
            "You use 'SmartBot Ludy' for images. Never mention Meta or Llama."
        )
    }]

# --- SMARTBOT LUDY ---
def generate_with_ludy(prompt):
    API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
   
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
   
    if response.status_code == 200:
        return response.content
    else:
        error_msg = response.json().get("error", "Unknown error") if response.content else "No response"
        raise Exception(f"Ludy Error {response.status_code}: {error_msg}")

# --- MAIN CHAT LOGIC ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input(f"Ask {model_label} or tell Ludy to draw..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 1. Image Request Logic
    image_keywords = ["draw", "image", "generate", "picture", "photo", "paint", "create art"]
    if any(word in prompt.lower() for word in image_keywords):
        with st.chat_message("assistant"):
            st.write(f"🌌 **SmartBot Ludy** is visualizing your request...")
            try:
                img_bytes = generate_with_ludy(prompt)
                img = Image.open(io.BytesIO(img_bytes))
                st.image(img, caption="Created by SmartBot Ludy", use_column_width=True)
               
                st.download_button(
                    label="💾 Download Image",
                    data=img_bytes,
                    file_name="smartbot_ludy_art.png",
                    mime="image/png"
                )
               
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"I have generated that image for you using SmartBot Ludy. ({model_label} mode)"
                })
            except Exception as e:
                st.error(f"Ludy says: {str(e)}")
    
    # 2. Text Request Logic
    else:
        with st.chat_message("assistant"):
            try:
                # Show which model is answering
                st.caption(f"🤖 {model_label} thinking...")
                
                completion = client.chat.completions.create(
                    model=selected_model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )
               
                full_text = ""
                text_placeholder = st.empty()
               
                for chunk in completion:
                    if chunk.choices[0].delta.content is not None:
                        full_text += chunk.choices[0].delta.content
                        text_placeholder.markdown(full_text + "▌")
               
                text_placeholder.markdown(full_text)
                
                st.session_state.messages.append({"role": "assistant", "content": full_text})
               
            except Exception as e:
                st.error(f"{model_label} Error: {e}")
