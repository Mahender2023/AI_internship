import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

# Validate API key
if not api_key:
    st.error("❌ No API key found. Please check your .env file.")
elif not api_key.startswith("sk-proj-"):
    st.warning("⚠️ API key does not start with 'sk-proj-'. Please double-check.")
elif api_key.strip() != api_key:
    st.warning("⚠️ API key has extra spaces. Please remove them.")
else:
    st.success("✅ API key looks good!")

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Streamlit UI
    st.title("💬 Chat with GPT-4o-mini")

    user_input = st.text_input("Enter your message to GPT:")

    if st.button("Send"):
        if user_input:
            with st.spinner("Getting response..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": user_input}]
                    )
                    st.markdown("**Response:**")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"API Error: {e}")
        else:
            st.warning("Please enter a message before sending.")
