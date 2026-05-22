# streamlit_app.py
import streamlit as st
import os
import tempfile
from doc_indexer import extract_text_from_pdf, chunk_text, build_faiss_index
from prompt_engine import retrieve_chunks, answer_question

st.set_page_config(page_title="📄 Document Analyzer", layout="wide")
st.title("📄 Document Analyzer — Open Source")

# --- File Upload ---
uploaded_files = st.file_uploader(
    "📂 Upload one or more PDFs", 
    type=["pdf"], 
    accept_multiple_files=True
)

# Initialize session state
if "indexed" not in st.session_state:
    st.session_state["indexed"] = False
    st.session_state["chunks"] = []
    st.session_state["indices"] = []

# --- Index Documents ---
if uploaded_files:
    if st.button("🚀 Index Documents"):
        all_chunks, all_indices = [], []
        for file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name

            st.info(f"📑 Processing **{file.name}** ...")
            text = extract_text_from_pdf(tmp_path)
            chunks = chunk_text(text)

            index, _ = build_faiss_index(chunks)
            all_chunks.extend(chunks)
            all_indices.append(index)

        st.session_state["chunks"] = all_chunks
        st.session_state["indices"] = all_indices
        st.session_state["indexed"] = True
        st.success("✅ Documents indexed!")

# --- Ask Questions ---
st.subheader("🔎 Ask Questions")
question = st.text_input("Type your question here:")

if question:
    if not st.session_state["indexed"]:
        st.warning("⚠️ Please upload and index documents first.")
    else:
        if st.button("Get Answer"):
            top_chunks = []
            for idx in st.session_state["indices"]:
                retrieved = retrieve_chunks(
                    question, 
                    st.session_state["chunks"], 
                    None, 
                    idx, 
                    top_k=2
                )
                top_chunks.extend(retrieved)

            answer = answer_question(question, top_chunks)

            st.markdown("### 📝 Answer")
            st.write(answer)

            with st.expander("📚 Supporting text chunks"):
                for c in top_chunks:
                    st.markdown(f"> {c}")
