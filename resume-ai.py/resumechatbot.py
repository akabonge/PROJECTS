import streamlit as st
from openai import OpenAI
import PyPDF2
from io import StringIO
import datetime
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.Secrets["OPENAI_API_KEY"])


# ✅ Your fine-tuned model ID
MODEL_ID = "ft:gpt-3.5-turbo-1106:resume-ai::BEpg7auE"

# === Streamlit UI ===
st.title("💼 Resume & Career AI Chatbot")
st.caption("Ask anything about job search, resumes, LinkedIn, interviews, or career growth.")

# === Optional: Upload Resume PDF ===
pdf_text = ""
uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])
if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    for page in reader.pages:
        pdf_text += page.extract_text()
    st.success("✅ Resume uploaded and processed.")

# === Start Session ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a professional and friendly AI Career Coach. "
                "Help users with resumes, job applications, interviews, LinkedIn, and career growth. "
                "Keep all replies focused on career topics."
            )
        }
    ]
    if pdf_text:
        st.session_state.messages.append({"role": "user", "content": f"Here is my resume:\n\n{pdf_text}\n\nGive me feedback."})

# === Chat input ===
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

# === Show chat history ===
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# === Export chat ===
if st.button("💾 Download chat log"):
    chat_log = "\n\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[1:])
    st.download_button("Download .txt", data=chat_log, file_name=f"career_chat_{datetime.date.today()}.txt", mime="text/plain")
