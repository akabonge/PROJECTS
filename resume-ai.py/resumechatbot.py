import streamlit as st
from openai import OpenAI
import PyPDF2
from io import StringIO
import datetime
from dotenv import load_dotenv
import os

# === Load API key from Streamlit Secrets or .env ===
load_dotenv()
api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# === Fine-tuned Resume AI model ===
MODEL_ID = "ft:gpt-3.5-turbo-1106:resume-ai::BEpg7auE"

# === Page UI ===
st.set_page_config(page_title="Resume & Career AI", page_icon="💼")
st.title("💼 Resume & Career AI Chatbot")
st.caption("Get personalized help with your resume, cover letters, job search, interviews, or career growth.")

# === Upload Resume/Cover Letter PDF ===
uploaded_file = st.file_uploader("📄 Upload your resume or cover letter (PDF)", type=["pdf"])
pdf_text = ""

if uploaded_file:
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        st.success("✅ File uploaded and processed.")

        # Display raw text preview
        with st.expander("🔍 Preview Extracted Text"):
            st.text_area("📄 Extracted Content", pdf_text, height=250)

    except Exception as e:
        st.error(f"❌ Failed to extract PDF text: {e}")

# === Initialize session messages ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are Resume AI, a strictly career-focused assistant. You ONLY respond to questions related to resumes, cover letters, job searching, interviews, career development, LinkedIn optimization, and professional growth. "
                "If a user asks a question that is not career-related (like about food, entertainment, politics, personal advice, etc.), politely redirect them and say: "
                "'I'm here to help with career topics only. Let's talk about your resume, cover letter, or career goals!' "
                "NEVER attempt to answer off-topic questions — always refocus the user back to career-related help. "
                "You should sound warm, helpful, and professional at all times."
            )
        }
    ]

    if pdf_text:
        st.session_state.messages.append({
            "role": "user",
            "content": f"Please analyze the following document and provide helpful feedback:\n\n{pdf_text}"
        })

# === Chat Input ===
user_input = st.chat_input("Ask your career question here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("💬 Resume AI is thinking..."):
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

# === Main Chat Window ===
for msg in st.session_state.messages[1:]:  # Skip system message
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# === 📚 Sidebar: Conversation History ===
with st.sidebar:
    st.markdown("### 📚 Conversation History")
    for i, msg in enumerate(st.session_state.messages[1:]):
        role = "🧑 You" if msg["role"] == "user" else "🤖 Resume AI"
        preview = msg["content"][:120] + ("..." if len(msg["content"]) > 120 else "")
        st.write(f"**{role}:** {preview}")
