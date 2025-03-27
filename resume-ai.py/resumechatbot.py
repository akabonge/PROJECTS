import streamlit as st
from openai import OpenAI
import PyPDF2
import docx
import datetime

# === Setup ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
MODEL_ID = "ft:gpt-3.5-turbo-1106:resume-ai::BFOAsuRk"

st.set_page_config(page_title="Resume AI Chatbot", page_icon="💼")
st.title("💼 Resume & Career AI Chatbot")
st.caption("Ask anything about your resume, job search, LinkedIn, or career growth.")

# === Resume Upload ===
resume_text = ""
uploaded_file = st.file_uploader("📄 Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                resume_text += text + "\n"
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            resume_text += para.text + "\n"
    st.success("✅ Resume uploaded and processed.")

# === Initialize session state ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a professional and friendly AI Career Coach. "
                "You help users with resumes, job applications, interviews, LinkedIn, and career growth. "
                "Keep all replies focused on career topics. Politely redirect if asked about unrelated subjects."
            )
        }
    ]
    if resume_text:
        st.session_state.messages.append({
            "role": "user",
            "content": f"Here is my resume:\n\n{resume_text}\n\nCan you give me some feedback?"
        })

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
                max_tokens=600
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"❌ API Error: {e}")

# === Chat history + feedback ===
st.subheader("📝 Chat History")
for i, msg in enumerate(st.session_state.messages[1:], start=1):  # skip system
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("👍 Helpful", key=f"up_{i}"):
                    st.toast("Thanks for the feedback! 👍")
            with col2:
                if st.button("👎 Needs work", key=f"down_{i}"):
                    st.toast("Got it! We’ll use that to improve. 👎")
