can you do this all for me but keeping in mind the real actual code to add it to. import streamlit as st
from openai import OpenAI
import PyPDF2
from io import StringIO
import datetime

# ✅ Load API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
MODEL_ID = "ft:gpt-3.5-turbo-1106:resume-ai::BFOAsuRk"

# === UI Title ===
st.set_page_config(page_title="Resume AI Chatbot", page_icon="💼")
st.title("💼 Resume & Career AI Chatbot")
st.caption("Ask anything about your resume, job search, LinkedIn, or career growth.")

# === PDF Upload ===
pdf_text = ""
uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])
if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    for page in reader.pages:
        pdf_text += page.extract_text()
    st.success("✅ Resume uploaded and processed.")

# === Chat session init ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a professional, career-focused AI assistant."
                " You help users with resume tips, job searching, LinkedIn, interview prep, and career growth only."
                " If the topic goes outside of careers, politely redirect back to career advice."
            )
        }
    ]
    if pdf_text:
        st.session_state.messages.append({"role": "user", "content": f"Here is my resume:\n\n{pdf_text}\n\nGive me feedback."})

# === Chat Input ===
user_input = st.chat_input("Ask your career question here...")
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
            st.error(f"❌ API Error: {e}")

# === Chat history display ===
for msg in st.session_state.messages[1:]:  # Skip system
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
