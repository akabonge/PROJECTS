import streamlit as st
from openai import OpenAI
import PyPDF2
import docx
import datetime

# === Load OpenAI client ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
MODEL_ID = "ft:gpt-3.5-turbo-1106:resume-ai::BFOAsuRk"
# === App config ===
st.set_page_config(page_title="Resume AI Chatbot", page_icon="💼")
st.title("💼 Resume & Career AI Chatbot")
st.caption("Ask anything about resumes, job search, LinkedIn, or career growth.")
    
# === Upload Resume ===
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

uploaded_file = st.file_uploader("📄 Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
if uploaded_file:
    resume_text = ""
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            resume_text += page.extract_text()
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            resume_text += para.text + "\n"
    st.session_state.resume_text = resume_text
    st.success("✅ Resume uploaded and saved.")

# === Initialize conversation ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a warm, professional AI career coach. "
                "You assist users with resumes, job search, LinkedIn, interviews, and career growth. "
                "Stay strictly on topic. If the user asks something unrelated to careers, politely guide them back."
            )
        }
    ]

 
        
    
# === Chat input ===
user_input = st.chat_input("Ask a career question...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Inject resume if resume uploaded and user asks about it
    if "resume" in user_input.lower() and st.session_state.resume_text:
        st.session_state.messages.append({
            "role": "user",
            "content": f"My resume is:\n\n{st.session_state.resume_text}"
        })

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

# === Display conversation history with feedback ===
st.subheader("📝 Chat History")
for i, msg in enumerate(st.session_state.messages[1:]):  # Skip system
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])
            feedback_key = f"feedback_{i}"
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("👍 Helpful", key=feedback_key+"_up"):
                    st.success("Thanks for the positive feedback!")
            with col2:
                if st.button("👎 Needs improvement", key=feedback_key+"_down"):
                    st.warning("Thanks for the feedback. We'll use this to improve.")
