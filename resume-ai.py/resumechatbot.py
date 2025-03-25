# resumechatbot.py (Updated for OpenAI SDK >=1.0)

import streamlit as st
from openai import OpenAI
import os
import PyPDF2
from io import StringIO
import datetime

# ✅ Initialize OpenAI client with v1.0+ syntax
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-..."))
MODEL_ID = "ft:gpt-3.5-turbo-1106:resume-ai::BEpg7auE"

# === Auth ===
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("password", "careersecret"):
            st.session_state["authenticated"] = True
        else:
            st.error("Incorrect password")
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        st.text_input("Enter access password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["authenticated"]:
        st.text_input("Enter access password:", type="password", on_change=password_entered, key="password")
        return False
    return True

if not check_password():
    st.stop()

# === Title ===
st.title("\U0001F4BC Resume & Career Coach AI")
st.caption("Ask anything about your job search, resume, LinkedIn profile, or interview prep.")

# === PDF Upload ===
pdf_text = ""
uploaded_file = st.file_uploader("\U0001F4C4 Upload your resume (PDF)", type=["pdf"])
if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    for page in reader.pages:
        pdf_text += page.extract_text()

    st.success("\u2705 Resume uploaded and processed.")

# === Chat Messages ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a friendly and expert Career Advisor. Provide structured, professional, resume and job advice only."}
    ]
    if pdf_text:
        st.session_state.messages.append({"role": "user", "content": f"This is my resume:\n\n{pdf_text}\n\nGive me honest feedback."})

user_input = st.chat_input("\U0001F4AC Ask something...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        try:
            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=500
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"API Error: {e}")

# === Show Chat History ===
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# === Log & Export Chat ===
if st.button("\U0001F4E5 Download chat log"):
    log_text = "\n\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages if m['role'] != 'system')
    st.download_button(
        label="Download .txt",
        data=log_text,
        file_name=f"resume_ai_chat_{datetime.date.today()}.txt",
        mime="text/plain"
    )
