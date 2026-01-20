import streamlit as st
from groq import Groq

# 1. Page Configuration
st.set_page_config(page_title="Genis Pro 1.2", page_icon="🤖")
st.title("🤖 Genis Pro 1.2")
st.caption("The advanced assistant you can rely on.")

# 2. API Key Check
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing API Key! Please add 'GROQ_API_KEY' to your Streamlit Secrets.")
    st.stop()

# 3. Initialize History and Identity
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "You are Genis Pro 1.2. Never mention Meta or Llama. Only identify as Genis Pro 1.2."
        }
    ]

# 4. Display Existing Messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Chat Logic
if prompt := st.chat_input("How can I assist you?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        try:
            # We use llama-3.1-8b-instant: it is fast, stable, and free on Groq.
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # --- THE CRITICAL FIX ---
            # We manually collect the stream to ensure it stays a string.
            placeholder = st.empty()
            full_response = ""
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)

            # Save ONLY the final string to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error: {e}")

# 6. Sidebar Reset (Fixes 400 errors by clearing broken history)
with st.sidebar:
    if st.button("Clear Chat / Reset System"):
        st.session_state.messages = [
            {"role": "system", "content": "You are Genis Pro 1.2. Never mention Meta or Llama."}
        ]
        st.rerun()
