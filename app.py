import streamlit as st
from groq import Groq
import google.generativeai as genai
from PIL import Image
import io

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
        gemini_key = st.secrets["GEMINI_API_KEY"]
        
        # Configure Gemini
        genai.configure(api_key=gemini_key)
        
        return groq_client, gemini_key
    except Exception as e:
        st.error(f"Missing API keys in Streamlit secrets: {str(e)}")
        st.info("You need: GROQ_API_KEY and GEMINI_API_KEY")
        st.stop()

client, GEMINI_KEY = get_clients()

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
    st.subheader("🎨 Ludy 2.0 - Nano Banana")
    st.success("✨ **Google Gemini Image Gen**\n\n"
              "🏆 Real Nano Banana & Pro!\n"
              "🆓 500-1,500 images/day FREE\n"
              "💳 No credit card needed\n"
              "⚡ Super fast generation\n"
              "🎯 State-of-the-art quality")
    
    # Model selection
    st.subheader("Image Model")
    image_model = st.selectbox(
        "Nano Banana Model",
        [
            "gemini-2.5-flash-image-preview",  # Nano Banana (500/day free)
            "gemini-3-pro-preview"              # Nano Banana Pro (limited free)
        ],
        index=0,
        format_func=lambda x: {
            "gemini-2.5-flash-image-preview": "🏆 Nano Banana (2.5 Flash) - 500/day FREE",
            "gemini-3-pro-preview": "💎 Nano Banana Pro (3.0) - Premium"
        }.get(x, x)
    )
    
    # Image settings
    st.subheader("Image Settings")
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["1:1", "16:9", "9:16", "4:3", "3:4"],
        index=0
    )
    
    st.caption(f"**Active Model:** {image_model.split('-')[0].title()} Image")
    st.caption(f"**Daily Limit:** {'500+ free' if '2.5' in image_model else '100 free'}")

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
    "You generate images using SmartBot Ludy 2.0, powered by Google's Gemini Image API. "
    "You have access to real 'Nano Banana' models (Gemini 2.5 Flash Image and Gemini 3 Pro Image). "
    "These are Google's state-of-the-art image generation models with 500-1,500 FREE images per day! "
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
#  LUDY 2.0 – GOOGLE GEMINI NANO BANANA
# ────────────────────────────────────────────────
def call_ludy_2_gemini(
    prompt: str,
    model_name: str = "gemini-2.5-flash-image-preview",
    aspect_ratio: str = "1:1"
) -> bytes:
    """
    Ludy 2.0 using Google's Gemini API with REAL Nano Banana models!
    
    Free tier: 500-1,500 images/day (no credit card!)
    Models:
    - gemini-2.5-flash-image-preview (Nano Banana) - 500/day
    - gemini-3-pro-preview (Nano Banana Pro) - limited
    """
    try:
        # Get the Gemini image model
        model = genai.GenerativeModel(model_name)
        
        # Map aspect ratios to dimensions
        dimensions_map = {
            "1:1": (1024, 1024),
            "16:9": (1024, 576),
            "9:16": (576, 1024),
            "4:3": (1024, 768),
            "3:4": (768, 1024)
        }
        width, height = dimensions_map.get(aspect_ratio, (1024, 1024))
        
        # Generate image
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
            }
        )
        
        # Extract image from response
        # Gemini returns image in response.parts
        if hasattr(response, 'parts') and response.parts:
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Get image bytes
                    image_data = part.inline_data.data
                    return image_data
        
        # If no image in parts, try text response with error
        if hasattr(response, 'text'):
            raise RuntimeError(f"No image generated. Response: {response.text[:200]}")
        
        raise RuntimeError("No image data in response")
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # Handle rate limiting
        if "quota" in error_msg or "limit" in error_msg or "429" in error_msg:
            raise RuntimeError(
                "🌙 **Daily Limit Reached!**\n\n"
                "Free tier limits:\n"
                "• Gemini 2.5 Flash Image: 500 images/day\n"
                "• Gemini 3 Pro: 100 images/day\n\n"
                "💡 **Resets:** Tomorrow at midnight UTC\n"
                "💰 **Upgrade:** Only $0.039 per image after free tier"
            )
        
        # Handle billing
        if "billing" in error_msg or "payment" in error_msg:
            raise RuntimeError(
                "💳 **Enable Billing for Higher Limits**\n\n"
                "Current: 500 free/day\n"
                "With billing: Only $0.039/image\n\n"
                "Enable at: https://console.cloud.google.com/billing"
            )
        
        # Handle model errors
        if "model" in error_msg or "not found" in error_msg:
            raise RuntimeError(
                f"⚠️ **Model Error**\n\n"
                f"Model '{model_name}' may not be available.\n"
                f"Try switching models in the sidebar.\n\n"
                f"Details: {str(e)[:200]}"
            )
        
        # Generic error
        raise RuntimeError(f"Ludy 2.0 (Gemini Nano Banana) error: {str(e)[:300]}")

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
            model_display_name = {
                "gemini-2.5-flash-image-preview": "Nano Banana (Gemini 2.5 Flash)",
                "gemini-3-pro-preview": "Nano Banana Pro (Gemini 3)"
            }.get(image_model, image_model)
            
            st.write(f"🌌 **Ludy 2.0** • {model_display_name} is creating your masterpiece...")
            st.caption("💡 Powered by Google Gemini - 100% FREE tier!")
            
            # Show generation details
            with st.expander("🎨 Generation Details", expanded=False):
                st.write(f"**Model:** {model_display_name}")
                st.write(f"**Aspect Ratio:** {aspect_ratio}")
                st.write(f"**Provider:** Google Gemini API")
                st.write(f"**Daily Free Limit:** {'500+' if '2.5' in image_model else '100'} images")
                st.write(f"**Cost After Free:** $0.039 per image")
            
            try:
                image_data = call_ludy_2_gemini(
                    prompt=user_input,
                    model_name=image_model,
                    aspect_ratio=aspect_ratio
                )
                
                image = Image.open(io.BytesIO(image_data))
                
                st.image(
                    image,
                    caption=f"✨ Ludy 2.0 · {model_display_name} · {aspect_ratio} · {display_name}",
                    use_column_width=True
                )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.download_button(
                        label="⬇️ Save Image (PNG)",
                        data=image_data,
                        file_name=f"ludy_2_nano_banana_{aspect_ratio.replace(':', 'x')}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                with col2:
                    st.success("✅ Done!")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Ludy 2.0 ({model_display_name} - Google Gemini) has created your image at {aspect_ratio}. ({display_name})"
                })
                
            except Exception as err:
                st.error(str(err))
                
                # Helpful tips
                if "limit" in str(err).lower():
                    st.info("💡 **Tips:**\n\n"
                           "1. Try again tomorrow when limits reset\n"
                           "2. Switch to the other Nano Banana model\n"
                           "3. Enable billing for only $0.039/image")
        
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

# ────────────────────────────────────────────────
#  FOOTER INFO
# ────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; opacity: 0.7;'>
<small>
🎨 <strong>Ludy 2.0</strong> powered by <strong>Google Gemini Nano Banana</strong><br>
✨ 500-1,500 FREE images/day • No credit card required<br>
🏆 State-of-the-art quality • Real Nano Banana Pro models
</small>
</div>
""", unsafe_allow_html=True)
