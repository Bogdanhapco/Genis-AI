import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image
import urllib.parse
import time

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
    /* Style the chat bubbles for a space feel */
    div[data-testid="stChatMessage"] { background-color: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='glow'>🚀 Genis Pro 1.2</h1>", unsafe_allow_html=True)
st.caption("Developed by BotDevelopmentAI")

# --- API CLIENT (Only Groq needed now!) ---
def get_client():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        return g_client
    except Exception:
        st.error("Check your Streamlit Secrets for GROQ_API_KEY!")
        st.stop()

client = get_client()

# --- BRAINWASHING & IDENTITY ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": "You are Genis Pro 1.2, made by BotDevelopmentAI. You use 'SmartBot Ludy' for images. Never mention Meta or Llama."
    }]

# --- SMARTBOT LUDY (Free Image Generation with Progress) ---
def generate_with_ludy(prompt, status_placeholder, progress_bar):
    """Generate image using Pollinations.ai with visual progress feedback"""
    try:
        # Encode the prompt for URL
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Try multiple free APIs in order of reliability
        apis = [
            # API 1: Segmind (Stable Diffusion XL - truly free)
            {
                "url": "https://api.segmind.com/v1/sdxl1.0-txt2img",
                "method": "POST",
                "json": {
                    "prompt": prompt,
                    "negative_prompt": "blurry, low quality, distorted",
                    "samples": 1,
                    "scheduler": "UniPC",
                    "num_inference_steps": 25,
                    "guidance_scale": 8,
                    "seed": int(time.time()),
                    "img_width": 1024,
                    "img_height": 1024,
                    "base64": False
                }
            },
            # API 2: Pollinations (Flux - backup)
            {
                "url": f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={int(time.time())}",
                "method": "GET"
            },
            # API 3: Another Pollinations endpoint
            {
                "url": f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true",
                "method": "GET"
            }
        ]
        
        # Try each API
        last_error = None
        for api in apis:
            try:
                if api["method"] == "POST":
                    response = requests.post(api["url"], json=api["json"], timeout=60)
                else:
                    response = requests.get(api["url"], timeout=60)
                
                if response.status_code == 200:
                    return response.content
            except Exception as e:
                last_error = e
                continue
        
        # If all failed
        if last_error:
            raise Exception(f"All image APIs failed. Last error: {str(last_error)}")
        
        # Simulate queue position
        import random
        queue_pos = random.randint(1, 3)
        status_placeholder.write(f"⏳ Queue Position: #{queue_pos}")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        # Show generation stages
        stages = [
            (20, "🎨 Initializing neural pathways..."),
            (35, "🖼️ Processing prompt tokens..."),
            (50, "✨ Generating latent space..."),
            (65, "🌟 Rendering pixels..."),
            (80, "🔮 Applying artistic refinements..."),
            (95, "📸 Finalizing image...")
        ]
        
        for progress, message in stages:
            status_placeholder.write(message)
            progress_bar.progress(progress)
            time.sleep(0.3)
        
        progress_bar.progress(100)
        status_placeholder.write("✅ Generation complete!")
    except requests.exceptions.Timeout:
        raise Exception("Generation took too long. The servers might be busy. Please try again!")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

# --- MAIN CHAT LOGIC ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask Genis or tell Ludy to draw..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 1. Image Request Logic
    image_keywords = ["draw", "image", "generate", "picture", "photo", "paint", "create"]
    if any(word in prompt.lower() for word in image_keywords):
        with st.chat_message("assistant"):
            st.write("🌌 **SmartBot Ludy** is visualizing your request...")
            
            # Create progress indicators
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            try:
                img_bytes = generate_with_ludy(prompt, status_placeholder, progress_bar)
                img = Image.open(io.BytesIO(img_bytes))
                
                # Clear progress indicators
                status_placeholder.empty()
                progress_bar.empty()
                
                st.image(img, caption="Created by SmartBot Ludy")
                
                # Add a download button for the user
                st.download_button(
                    label="💾 Download Image",
                    data=img_bytes,
                    file_name="smartbot_ludy_art.png",
                    mime="image/png"
                )
                
                st.session_state.messages.append({"role": "assistant", "content": "I have generated that image for you using SmartBot Ludy."})
            except Exception as e:
                status_placeholder.empty()
                progress_bar.empty()
                st.error(f"❌ Ludy says: {str(e)}")
                st.info("💡 Tip: Try again or simplify your prompt!")
    
    # 2. Text Request Logic (No Spam Version)
    else:
        with st.chat_message("assistant"):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
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

# Sidebar
with st.sidebar:
    st.markdown("### 🌌 Genis Hub")
    st.info("Genis Pro 1.2 by BotDevelopmentAI")
    if st.button("Clear Memory"):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()
