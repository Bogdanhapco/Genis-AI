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
    st.subheader("🎨 Ludy 2.0")
    st.success("✨ **Google Gemini/Imagen**\n\n"
              "🆓 Gemini Flash - FREE!\n"
              "💎 Imagen - $0.02/image\n"
              "🏆 State-of-the-art quality")
    
    # Model selection
    st.subheader("Image Model")
    image_model = st.selectbox(
        "Choose Model",
        [
            "gemini-2.0-flash-exp",           # FREE - Flash with image gen
            "imagen-4.0-fast-generate-001",   # $0.02 per image
            "imagen-4.0-generate-001"         # $0.03 per image
        ],
        index=0,
        format_func=lambda x: {
            "gemini-2.0-flash-exp": "🆓 Gemini Flash - FREE (with text output)",
            "imagen-4.0-fast-generate-001": "⚡ Imagen 4 Fast - $0.02/img",
            "imagen-4.0-generate-001": "💎 Imagen 4 - $0.03/img (best quality)"
        }.get(x, x)
    )
    
    # Settings based on model type
    is_gemini = "gemini" in image_model
    
    if not is_gemini:  # Imagen models
        st.subheader("Image Settings")
        aspect_ratio = st.selectbox(
            "Aspect Ratio",
            ["1:1", "16:9", "9:16", "4:3", "3:4"],
            index=0
        )
        num_images = st.slider("Number of Images", 1, 4, 1)
    
    st.caption(f"**Active:** {image_model.split('-')[0].title()}")

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
    "You generate images using SmartBot Ludy 2.0, powered by Google's Gemini and Imagen models. "
    "You have access to: Gemini Flash (FREE with image generation), Imagen 4 Fast ($0.02/image), "
    "and Imagen 4 ($0.03/image for best quality). "
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
#  LUDY 2.0 – GOOGLE GEMINI/IMAGEN
# ────────────────────────────────────────────────
def call_ludy_2_gemini_flash(prompt: str) -> bytes:
    """
    Use Gemini Flash with image generation - 100% FREE!
    Note: This also generates text along with the image
    """
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        
        # Extract image from response
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data
        
        raise RuntimeError("No image generated in response")
        
    except Exception as e:
        raise RuntimeError(f"Gemini Flash error: {str(e)[:300]}")

def call_ludy_2_imagen(
    prompt: str, 
    model: str = "imagen-4.0-fast-generate-001",
    aspect_ratio: str = "1:1",
    num_images: int = 1
) -> list:
    """
    Use Imagen models - Paid but cheap ($0.02-0.03/image)
    Returns list of image bytes
    """
    try:
        # Map aspect ratios
        aspect_map = {
            "1:1": "1:1",
            "16:9": "16:9",
            "9:16": "9:16",
            "4:3": "4:3",
            "3:4": "3:4"
        }
        
        response = gemini_client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=num_images,
                aspect_ratio=aspect_map.get(aspect_ratio, "1:1")
            )
        )
        
        # Extract images
        images = []
        for image_part in response.generated_images:
            if hasattr(image_part, 'image') and image_part.image:
                # Convert PIL image to bytes
                img_byte_arr = io.BytesIO()
                image_part.image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                images.append(img_byte_arr.getvalue())
        
        if not images:
            raise RuntimeError("No images generated")
        
        return images
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if "quota" in error_msg or "limit" in error_msg:
            raise RuntimeError(
                "💳 **Billing Required**\n\n"
                "Imagen models require enabled billing.\n"
                "Cost: $0.02-0.03 per image (very cheap!)\n\n"
                "Enable at: https://console.cloud.google.com/billing"
            )
        
        raise RuntimeError(f"Imagen error: {str(e)[:300]}")

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
            model_display = {
                "gemini-2.0-flash-exp": "Gemini Flash (FREE)",
                "imagen-4.0-fast-generate-001": "Imagen 4 Fast ($0.02)",
                "imagen-4.0-generate-001": "Imagen 4 ($0.03)"
            }.get(image_model, image_model)
            
            st.write(f"🌌 **Ludy 2.0** • {model_display} is creating...")
            
            try:
                if "gemini" in image_model:
                    # Gemini Flash - FREE!
                    image_data = call_ludy_2_gemini_flash(user_input)
                    image = Image.open(io.BytesIO(image_data))
                    
                    st.image(image, caption=f"✨ Ludy 2.0 · {model_display} · {display_name}", use_column_width=True)
                    
                    st.download_button(
                        label="⬇️ Save Image (PNG)",
                        data=image_data,
                        file_name="ludy_2_gemini_flash.png",
                        mime="image/png"
                    )
                    
                    st.success(f"✅ Generated FREE with Gemini Flash!")
                    
                else:
                    # Imagen - Paid but cheap
                    images = call_ludy_2_imagen(
                        user_input,
                        model=image_model,
                        aspect_ratio=aspect_ratio,
                        num_images=num_images
                    )
                    
                    for idx, img_data in enumerate(images):
                        image = Image.open(io.BytesIO(img_data))
                        
                        st.image(image, caption=f"✨ Ludy 2.0 · {model_display} · Image {idx+1}/{len(images)}", use_column_width=True)
                        
                        st.download_button(
                            label=f"⬇️ Save Image {idx+1}",
                            data=img_data,
                            file_name=f"ludy_2_imagen_{idx+1}.png",
                            mime="image/png",
                            key=f"download_{idx}"
                        )
                    
                    cost = 0.02 if "fast" in image_model else 0.03
                    total_cost = cost * len(images)
                    st.info(f"💰 Cost: ${total_cost:.2f} ({len(images)} image{'s' if len(images) > 1 else ''} × ${cost})")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Ludy 2.0 ({model_display}) has created your image. ({display_name})"
                })
                
            except Exception as err:
                st.error(str(err))
                
                if "billing" in str(err).lower():
                    st.info("💡 **Try FREE option:**\n"
                           "Switch to 'Gemini Flash' in sidebar for FREE image generation!")
        
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
🎨 <strong>Ludy 2.0</strong> powered by <strong>Google Gemini & Imagen</strong><br>
✨ Gemini Flash: FREE • Imagen 4 Fast: $0.02/image • Imagen 4: $0.03/image
</small>
</div>
""", unsafe_allow_html=True)
