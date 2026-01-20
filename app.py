import streamlit as st
from groq import Groq

# 1. Setup the Page
st.set_page_config(page_title="Genis Pro 1.2", page_icon="🤖")
st.title("🤖 Genis Pro 1.2")
st.caption("Always active. Always smart.")

# 2. Secure API Connection
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing API Key! Add 'GROQ_API_KEY' to your Streamlit Secrets.")
    st.stop()

# 3. Identity Control (The "Brainwash" Prompt)
# This keeps the AI focused on being Genis Pro 1.2
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "Your name is Genis Pro 1.2. You are a highly advanced AI. "
                "NEVER say you are Meta, Llama, or an AI trained by Facebook. "
                "If asked who you are, strictly say: 'I am Genis Pro 1.2, your advanced assistant.' "
                "Keep your identity consistent and professional."
            )
        }
    ]

# 4. Display Chat History
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Handle User Input
if prompt := st.chat_input("Message Genis Pro..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 6. Generate Response with Safety Catch
    with st.chat_message("assistant"):
        try:
            # Model: 'llama-3.1-8b-instant' is the 2026 standard for fast/free Groq use
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages,
                stream=True,
            )
            
            # Write response to screen and capture the output
            raw_response = st.write_stream(stream)
            
            # --- THE FIX FOR THE 400 ERROR ---
            # We must force the response to be a string before saving it.
            # If it's a generator or NULL, this converts it to text so Groq doesn't crash later.
            clean_response = str(raw_response) if raw_response else "I encountered a glitch. Please try again."

            # Save clean text to history
            st.session_state.messages.append({"role": "assistant", "content": clean_response})
            
        except Exception as e:
            st.error(f"System Error: {e}")

# 7. Sidebar Reset (Optional but helpful)
with st.sidebar:
    if st.button("Clear Chat / Reset Identity"):
        st.session_state.messages = []
        st.rerun()
