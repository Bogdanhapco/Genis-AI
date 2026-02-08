import streamlit as st
from groq import Groq
from together import Together
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
        # Together AI for Nano Banana Pro
        together_client = Together(api_key=st.secrets["TOGETHER_API_KEY"])
        return groq_client, together_client
    except Exception as e:
        st.error(f"Missing API keys in Streamlit secrets: {str(e)}")
        st.stop()

client, together_client = get_clients()

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
    
    st.divider()
    st.subheader("🎨 Ludy 2.0 Nano Banana Pro")
    st.success("✨ **Google Gemini 2.5 Flash Image**\n\n"
              "🎯 State-of-the-art quality\n"
              "📝 Perfect text rendering\n"
              "👤 Character consistency\n"
              "⚡ Lightning fast")
    st.caption("⚠️ Free tier: ~100 images/day")
    
    # Image settings
    st.subheader("Image Settings")
    img_width = st.selectbox("Width", [1024, 768, 512], index=0)
    img_height = st.selectbox("Height", [768, 1024, 512], index=0)
    img_steps = st.slider("Quality Steps", 8, 50, 28, help="Higher = better quality, slower")

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
    "You generate images using SmartBot Ludy 2.0, powered by Nano Banana Pro "
    "(Google's Gemini 2.5 Flash Image model). This is a state-of-the-art image generator "
    "known for exceptional quality, perfect text rendering, and character consistency. "
    "When asked to draw, create, generate images, pictures, art, etc., you use Ludy 2.0. "
    "Stay in character. Be helpful, concise when appropriate, and maximally intelligent."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": current_system_prompt
    }]
elif not st.session_state.messages:
    st.session_state.messages.append({
        "role": "system",
        "content": current_system_prompt
    })

st.session_state.messages[0]["content"] = current_system_prompt

with st.sidebar:
    st.caption(f"Active Identity: **{display_name}**")

# ────────────────────────────────────────────────
#  LUDY 2.0 – NANO BANANA PRO (TOGETHER AI)
# ────────────────────────────────────────────────
def call_ludy_2_pro(prompt: str, width: int = 1024, height: int = 768, steps: int = 28):
    """
    Ludy 2.0 using genuine Nano Banana Pro via Together AI
    Model: google/gemini-3-pro-image (Nano Banana Pro)
    """
    try:
        response = together_client.images.generate(
            model="google/gemini-3-pro-image",
            prompt=prompt,
            width=width,
            height=height,
            steps=steps,
            n=1
        )
        
        # Get the image URL
        image_url = response.data[0].url
        
        # Download the image
        import requests
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        return img_response.content
        
    except Exception as e:
        error_msg = str(e)
        # Handle rate limiting gracefully
        if "rate limit" in error_msg.lower() or "quota" in error_msg.lower() or "429" in error_msg:
            raise RuntimeError(
                "🌙 Ludy 2.0 has reached its daily generation limit!\n\n"
                "Free tier allows ~100 images/day. Limit resets in 24 hours.\n"
                "Consider upgrading to Together AI's paid tier for unlimited access."
            )
        elif "credit" in error_msg.lower():
            raise RuntimeError(
                "💳 Together AI credits depleted.\n\n"
                "Add credits at: https://api.together.xyz/settings/billing"
            )
        raise RuntimeError(f"Ludy 2.0 (Nano Banana Pro) error: {error_msg}")

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
if user_input := st.chat_input(f"Talk to {display_name} • draw with Ludy 2.0..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    image_triggers = ["draw", "image", "generate", "picture", "photo", "paint", "art", "create image", "make me"]
    is_image_request = any(word in user_input.lower() for word in image_triggers)

    with st.chat_message("assistant"):
        if is_image_request:
            st.write(f"🌌 **Ludy 2.0** • Nano Banana Pro is creating your masterpiece...")
            
            # Show generation settings
            with st.expander("🎨 Generation Details", expanded=False):
                st.write(f"**Model:** Google Gemini 2.5 Flash Image (Nano Banana Pro)")
                st.write(f"**Resolution:** {img_width}x{img_height}px")
                st.write(f"**Quality Steps:** {img_steps}")
            
            try:
                image_data = call_ludy_2_pro(
                    prompt=user_input,
                    width=img_width,
                    height=img_height,
                    steps=img_steps
                )
                image = Image.open(io.BytesIO(image_data))
                
                # Display with enhanced caption
                st.image(
                    image, 
                    caption=f"✨ Ludy 2.0 · Nano Banana Pro · {img_width}x{img_height} · {display_name}",
                    use_column_width=True
                )
                
                # Download button
                st.download_button(
                    label="⬇️ Save Image (PNG)",
                    data=image_data,
                    file_name="ludy_2_nano_banana_pro.png",
                    mime="image/png",
                    use_container_width=False
                )
                
                st.success("✅ Image generated successfully with Nano Banana Pro!")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Ludy 2.0 (Nano Banana Pro - Google Gemini) has created your image at {img_width}x{img_height}px. ({display_name})"
                })
                
            except Exception as err:
                st.error(str(err))
                
                # Helpful recovery suggestions
                if "limit" in str(err).lower():
                    st.info("💡 **What you can do:**\n"
                           "1. Try again tomorrow when limits reset\n"
                           "2. Upgrade to Together AI Pro ($20/month for unlimited)\n"
                           "3. Get free $5 credits at: https://api.together.xyz")
                elif "credit" in str(err).lower():
                    st.info("💡 **Get more credits:**\n"
                           "Add credits at: https://api.together.xyz/settings/billing\n"
                           "New users get $5 free!")
        
        else:
            # Regular chat response
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
