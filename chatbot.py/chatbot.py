import streamlit as st
import openai
from pinecone import Pinecone

# === Load credentials from Streamlit secrets ===
openai.api_key = st.secrets["OPENAI_API_KEY"]
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
index = pc.Index("fcc-chatbot-index")

# === Streamlit app layout ===
st.set_page_config(page_title="📡 FCC Regulatory ChatBot", layout="wide")
st.title("📡 FCC Regulatory Assistant")
st.markdown("Ask questions about emergency alerts, public safety systems, or FCC policies.")

query = st.text_input("💬 Enter your question:")

if query:
    with st.spinner("Thinking..."):

        # Step 1: Embed user query
        embed_response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_vector = embed_response["data"][0]["embedding"]

        # Step 2: Query Pinecone
        results = index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True
        )

        # Step 3: Collect context from results
        context_chunks = [match["metadata"]["text"] for match in results["matches"]]
        full_context = "\n\n".join(context_chunks)

        # Step 4: Build prompt for OpenAI
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

        # Step 5: Ask OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        # Step 6: Display response
        answer = response["choices"][0]["message"]["content"]
        st.markdown("### 🤖 ChatBot Response")
        st.write(answer)

        # Optional: Show source context
        with st.expander("📄 View Retrieved Chunks"):
            for i, chunk in enumerate(context_chunks, 1):
                st.markdown(f"**Chunk {i}**")
                st.write(chunk)
