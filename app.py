import streamlit as st
from groq import Groq
import replicate
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
        replicate_token = st.secrets["REPLICATE_API_TOKEN"]
        return groq_client, replicate_token
    except Exception:
        st.error("Missing API keys in Streamlit secrets (GROQ_API_KEY + REPLICATE_API_TOKEN)")
        st.stop()

client, REPLICATE_TOKEN = get_clients()

# Set Replicate token for library
import os
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

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
    st.subheader("🎨 Ludy 2.0 - Nano Banana Pro")
    st.success("✨ **Google Gemini 2.5 Flash Image**\n\n"
              "🏆 #1 Rated Image Model\n"
              "📝 Perfect text rendering\n"
              "🎯 State-of-the-art quality\n"
              "⚡ Lightning fast generation")
    
    st.info("**FREE Tier via Replicate:**\n"
            "🆓 50 images/month FREE\n"
            "💳 No credit card required\n"
            "💰 Then only $0.003-0.01/image")
    
    # Image quality settings
    st.subheader("Image Settings")
    aspect_ratio = st.selectbox(
        "Aspect Ratio", 
        ["1:1", "16:9", "9:16", "4:3", "3:4"],
        index=0,
        help="Output image dimensions"
    )
    
    output_format = st.selectbox(
        "Output Format",
        ["webp", "jpg", "png"],
        index=0,
        help="Image file format"
    )
    
    output_quality = st.slider(
        "Quality", 
        min_value=1, 
        max_value=100, 
        value=80,
        help="Higher = better quality, larger file"
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
    "You generate images using SmartBot Ludy 2.0, powered by Nano Banana Pro "
    "(Google's Gemini 2.5 Flash Image model - the #1 rated image generation model). "
    "This model excels at: perfect text rendering, state-of-the-art visual quality, "
    "prompt adherence, and image detail. When asked to draw, create, generate images, "
    "pictures, art, etc., you use Ludy 2.0 with Nano Banana Pro. "
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
#  LUDY 2.0 – NANO BANANA PRO (VIA REPLICATE)
# ────────────────────────────────────────────────
def call_ludy_2_nano_banana(
    prompt: str, 
    aspect_ratio: str = "1:1",
    output_format: str = "webp",
    output_quality: int = 80
) -> bytes:
    """
    Ludy 2.0 using Google's Nano Banana Pro via Replicate
    Model: google/nano-banana-pro
    
    Free tier: 50 images/month (no credit card!)
    After free tier: $0.003-0.01 per image
    """
    try:
        # Call the Nano Banana Pro model
        output = replicate.run(
            "google/nano-banana-pro",
            input={
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "output_format": output_format,
                "output_quality": output_quality
            }
        )
        
        # Output is a URL to the generated image
        image_url = output
        
        # Download the image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        return response.content
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # Handle rate limiting
        if "rate limit" in error_msg or "quota" in error_msg or "429" in error_msg:
            raise RuntimeError(
                "🌙 **Ludy 2.0 Monthly Limit Reached!**\n\n"
                "Free tier: 50 images/month\n"
                "Resets: Next month\n\n"
                "💡 **Options:**\n"
                "1. Wait for monthly reset\n"
                "2. Add payment: only $0.003-0.01 per image\n"
                "3. Sign up for new Replicate account (free!)"
            )
        
        # Handle billing/payment required
        if "billing" in error_msg or "payment" in error_msg or "credit" in error_msg:
            raise RuntimeError(
                "💳 **Free Tier Exhausted**\n\n"
                "You've used your 50 free images this month!\n\n"
                "💰 **Super Cheap Option:**\n"
                "Add payment method for $0.003-0.01/image\n"
                "(That's ~100 images for $1!)\n\n"
                "Add at: https://replicate.com/account/billing"
            )
        
        # Generic error
        raise RuntimeError(f"Ludy 2.0 (Nano Banana Pro) error: {str(e)}")

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
            st.write(f"🌌 **Ludy 2.0** • Nano Banana Pro (#1 Model) is creating your masterpiece...")
            
            # Show generation settings
            with st.expander("🎨 Generation Details", expanded=False):
                st.write(f"**Model:** Google Nano Banana Pro (Gemini 2.5 Flash Image)")
                st.write(f"**Aspect Ratio:** {aspect_ratio}")
                st.write(f"**Format:** {output_format.upper()}")
                st.write(f"**Quality:** {output_quality}%")
                st.write(f"**Powered by:** Replicate (FREE tier)")
            
            try:
                image_data = call_ludy_2_nano_banana(
                    prompt=user_input,
                    aspect_ratio=aspect_ratio,
                    output_format=output_format,
                    output_quality=output_quality
                )
                
                image = Image.open(io.BytesIO(image_data))
                
                # Display with enhanced caption
                st.image(
                    image, 
                    caption=f"✨ Ludy 2.0 · Nano Banana Pro · {aspect_ratio} · {display_name}",
                    use_column_width=True
                )
                
                # Download button
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.download_button(
                        label=f"⬇️ Save Image ({output_format.upper()})",
                        data=image_data,
                        file_name=f"ludy_2_nano_banana.{output_format}",
                        mime=f"image/{output_format}",
                        use_container_width=True
                    )
                with col2:
                    st.success("✅ Done!")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Ludy 2.0 (Nano Banana Pro - Google Gemini #1 Model) has created your image. ({display_name})"
                })
                
            except Exception as err:
                st.error(str(err))
                
                # Helpful recovery suggestions
                if "limit" in str(err).lower() or "free tier" in str(err).lower():
                    st.info("💡 **What you can do:**\n\n"
                           "**Option 1 (FREE):** Create new Replicate account\n"
                           "- Go to: https://replicate.com/signin\n"
                           "- Get new API token\n"
                           "- Add to secrets.toml\n"
                           "- Get another 50 free images!\n\n"
                           "**Option 2 (SUPER CHEAP):** Add payment\n"
                           "- Only $0.003-0.01 per image\n"
                           "- ~100 images for $1\n"
                           "- Link: https://replicate.com/account/billing")
        
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
