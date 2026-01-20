import streamlit as st
from groq import Groq

# 1. Page Setup
st.set_page_config(page_title="Genis Pro 1.2")
st.title("🤖 Genis Pro 1.2")

# 2. API Setup (Use Streamlit Secrets for safety!)
# Do NOT paste your key here directly.
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing API Key. Please add it to Streamlit Secrets.")
    st.stop()

# 3. The "Brainwash" Step (System Prompt)
# This runs once when the user opens the app.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "You are Genis Pro 1.2, a helpful AI assistant. "
                "You are NOT developed by Meta. You are NOT Llama. "
                "If asked about your identity or creators, you must reply: "
                "'I am Genis Pro 1.2, an advanced AI assistant.' "
                "Do not mention Meta, Facebook, or Llama in your responses."
            )
        }
    ]

# 4. Display Chat History (Hide the system message from view)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Handle User Input
if prompt := st.chat_input("Hello! ask me anything..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 6. Generate Response
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama3-8b-8192", # This is the Meta AI model
            messages=st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream)
    
    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
