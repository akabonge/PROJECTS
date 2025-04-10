import streamlit as st
from openai import OpenAI
from pinecone import Pinecone

# === Setup clients ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
index = pc.Index("fcc-chatbot-index")

# === Layout ===
st.set_page_config(page_title="📡 FCC Regulatory ChatBot", layout="wide")
st.title("📡 FCC Regulatory Assistant")
st.markdown("Ask questions about emergency alerts, public safety systems, or FCC policies.")

# === Session state for full chat history ===
if "messages" not in st.session_state:
    st.session_state.messages = []

# === Chat input ===
query = st.text_input("💬 Enter your question:")

if query:
    with st.spinner("Thinking..."):

        # Step 1: Embed the query
        embed_response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=[query]
        )
        query_vector = embed_response.data[0].embedding

        # Step 2: Query Pinecone
        results = index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True
        )

        # Step 3: Extract context
        context_chunks = [match["metadata"]["text"] for match in results["matches"]]
        full_context = "\n\n".join(context_chunks)

        # Step 4: Build prompt
        system_prompt = (
            "You are a domain-specific assistant trained solely on emergency alert systems, "
            "public safety communications, cybersecurity policy, disaster response frameworks, and FCC regulatory principles. "
            "Answer based only on the provided source material. Do not guess or use external knowledge."
        )

        user_prompt = f"""Using the following source material, answer the user's question.

---SOURCE MATERIAL---
{full_context}

---USER QUESTION---
{query}
"""

        # Step 5: Get OpenAI response
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        answer = chat_response.choices[0].message.content

        # Step 6: Save both user and bot messages
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.messages.append({"role": "assistant", "content": answer})

# === Display full chat history ===
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"👤 **You:** {message['content']}")
    else:
        st.markdown(f"🤖 **Bot:** {message['content']}")
