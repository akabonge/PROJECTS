import streamlit as st
import openai

# ✅ Set your OpenAI API key directly (safe for local use only)
openai.api_key = "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"

# ✅ Your fine-tuned model ID
MODEL_ID = "ft:gpt-3.5-turbo-1106:resume-ai::BEpg7auE"

# App title
st.title("💼 Career & Resume AI Chatbot")
st.caption("Ask me anything about resumes, job search, interviews, or career growth!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful, professional AI Career Advisor. "
                "You help users with resumes, job search strategies, interviews, career transitions, LinkedIn profiles, and professional growth. "
                "Keep responses focused only on career topics."
            )
        }
    ]

# Capture user message
user_input = st.chat_input("What would you like help with today?")

# Call OpenAI and display reply
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        try:
            response = openai.ChatCompletion.create(
                model=MODEL_ID,
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=500
            )
            ai_reply = response['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        except Exception as e:
            st.error(f"Error: {e}")

# Display message history
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
