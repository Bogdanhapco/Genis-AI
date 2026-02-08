import streamlit as st
from groq import Groq
from google import genai
from google.genai import types
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
        gemini_key = st.secrets["GEMINI_API_KEY"]
        gemini_client = genai.Client(api_key=gemini_key)
        return groq_client, gemini_client
    except Exception as e:
        st.error(f"Missing API keys: {str(e)}")
        st.info("You need: GROQ_API_KEY and GEMINI_API_KEY")
        st.stop()

client, gemini_client = get_clients()

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
    st.subheader("🍌 Ludy 2.0 - Nano Banana")
    st.success("✨ **Google Gemini 2.5 Flash Image**\n\n"
              "🍌 Real Nano Banana!\n"
              "🆓 FREE tier available\n"
              "⚡ Lightning fast generation\n"
              "🎯 State-of-the-art quality\n"
              "📝 Perfect text rendering")
    
    st.caption("Powered by: Gemini 2.5 Flash Image")

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
    "You generate images using SmartBot Ludy 2.0, powered by Google's Nano Banana "
    "(Gemini 2.5 Flash Image) - Google's state-of-the-art image generation model. "
    "Nano Banana excels at: perfect text rendering, character consistency, scene logic, "
    "multi-image blending, and natural language understanding. "
    "When asked to draw, create, generate images, pictures, art, etc., you use Ludy 2.0 with Nano Banana. "
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
#  LUDY 2.0 – NANO BANANA (REAL!)
# ────────────────────────────────────────────────
def call_ludy_2_nano_banana(prompt: str) -> bytes:
    """
    Ludy 2.0 using REAL Nano Banana (Gemini 2.5 Flash Image)
    
    This is the actual model used in Gemini for image generation!
    Free tier available with quotas.
    """
    try:
        # Call the REAL Nano Banana model
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            )
        )
        
        # Extract image from response
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data
        
        raise RuntimeError("No image generated in response")
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # Handle quota/rate limiting
        if "quota" in error_msg or "limit" in error_msg or "429" in error_msg:
            raise RuntimeError(
                "🍌 **Nano Banana Daily Limit Reached!**\n\n"
                "Free tier has daily quotas.\n"
                "Limits reset daily.\n\n"
                "💡 **Options:**\n"
                "1. Wait for tomorrow's reset\n"
                "2. Upgrade to Google AI Plus for higher quotas\n"
                "3. Use Gemini web app (gemini.google.com) for free access"
            )
        
        # Handle billing
        if "billing" in error_msg or "payment" in error_msg:
            raise RuntimeError(
                "💳 **Enable Billing for API Access**\n\n"
                "Nano Banana is free in Gemini web app,\n"
                "but API may have different limits.\n\n"
                "Try: gemini.google.com (free!)"
            )
        
        # Generic error
        raise RuntimeError(f"Nano Banana error: {str(e)[:300]}")

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
            st.write(f"🍌 **Ludy 2.0** • Nano Banana is creating your masterpiece...")
            st.caption("💡 Powered by Google Gemini 2.5 Flash Image")
            
            try:
                with st.spinner("Generating with Nano Banana..."):
                    image_data = call_ludy_2_nano_banana(user_input)
                
                image = Image.open(io.BytesIO(image_data))
                
                st.image(
                    image,
                    caption=f"🍌 Ludy 2.0 · Nano Banana · {display_name}",
                    use_column_width=True
                )
                
                st.download_button(
                    label="⬇️ Save Image (PNG)",
                    data=image_data,
                    file_name="ludy_2_nano_banana.png",
                    mime="image/png"
                )
                
                st.success("✅ Generated with Nano Banana (Gemini 2.5 Flash Image)!")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Ludy 2.0 (Nano Banana - Google Gemini 2.5 Flash Image) has created your image. ({display_name})"
                })
                
            except Exception as err:
                st.error(str(err))
                
                if "limit" in str(err).lower():
                    st.info("💡 **Alternative:**\n"
                           "Visit gemini.google.com and select '🍌Create images' for FREE unlimited access!")
        
        else:
            # Regular chat
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
#  FOOTER
# ────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align: center; opacity: 0.7;'>
<small>
🍌 <strong>Ludy 2.0</strong> powered by <strong>Nano Banana</strong> (Google Gemini 2.5 Flash Image)<br>
✨ State-of-the-art image generation · Perfect text rendering · Character consistency
</small>
</div>
""", unsafe_allow_html=True)
