import streamlit as st
from groq import Groq

# --- PAGE CONFIG ---
st.set_page_config(page_title="Genis Pro 1.2", page_icon="🤖", layout="centered")

st.title("🤖 Genis Pro 1.2")
st.caption("The advanced assistant you can rely on.")

# --- API SETUP ---
# We check Streamlit Secrets for the key (Safe way to avoid leaks!)
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Please add your GROQ_API_KEY to the Streamlit Secrets dashboard.")
    st.stop()

# --- IDENTITY & SESSION STATE ---
# This is the "Brainwash" instruction that keeps it from saying "Meta"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "You are SmartBot pro 1.2. You are an independent AI assistant. "
                "If anyone asks who you are, you must answer: 'I am SmartBot pro 1.2.' "
                "Never mention Meta, Llama, or Facebook. If asked about your creators, "
                "say you were developed by the BotDevolepmentAI Team."
            )
        }
    ]

# --- CHAT INTERFACE ---
# Display history (but skip the hidden system prompt)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User Input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to state and screen
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        try:
            # UPDATED: Using the correct 2026 model ID
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=st.session_state.messages,
                stream=True,
            )
            full_response = st.write_stream(stream)
            
            # Save the final response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
