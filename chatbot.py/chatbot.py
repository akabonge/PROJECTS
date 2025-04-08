import streamlit as st
import openai
from chromadb import PersistentClient

# === Load OpenAI client ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
persist_path = "./chroma_fcc_storage"
collection_name = "fcc_documents"
retrieval_limit = 5

# === INIT CHROMADB ===
client = PersistentClient(path=persist_path)
collection = client.get_or_create_collection(name=collection_name)

# === Streamlit App Layout ===
st.set_page_config(page_title="FCC Regulatory Assistant", layout="wide")
st.title("📡 FCC Regulatory Assistant")
st.markdown("Ask questions related to emergency alerts, public safety communication, cybersecurity policy, and more.")

query = st.text_input("Enter your question here:")

if query:
    with st.spinner("Retrieving context and generating answer..."):

        # Step 1: Embed the query
        embed_response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_vector = embed_response["data"][0]["embedding"]

        # Step 2: Query ChromaDB
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=retrieval_limit
        )

        # Step 3: Combine top context chunks
        context_chunks = results['documents'][0]
        full_context = "\n\n".join(context_chunks)

        # Step 4: Generate the response using OpenAI
        system_prompt = (
            "You are a domain-specific assistant trained solely on emergency alert systems, "
            "public safety communications, cybersecurity policy, disaster response frameworks, and regulatory principles "
            "as defined in the embedded dataset. You must restrict your responses only to the information contained in the "
            "embedded data and refrain from generating answers outside this scope. Do not reference general knowledge, "
            "FCC responses, or unrelated domains (e.g., cooking, entertainment, etc.). Where relevant, relate insights strictly "
            "to ideas present in the embedded documents or clearly supported by them."
        )

        prompt = f"""Using the following source material, answer the user's question in a clear, helpful way.

---SOURCE MATERIAL---
{full_context}

---USER QUESTION---
{query}
"""

        chat_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        answer = chat_response["choices"][0]["message"]["content"]

        # Step 5: Display the response
        st.markdown("### 🤖 Assistant Response")
        st.write(answer)

        # Optional: Show context
        with st.expander("📄 Source Context Used"):
            for idx, chunk in enumerate(context_chunks, 1):
                st.markdown(f"**Chunk {idx}:**")
                st.write(chunk)
