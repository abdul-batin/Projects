# qa_engine.py
from transformers import pipeline
import numpy as np
from sentence_transformers import SentenceTransformer

# Load a lightweight QA model (only once)
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

def retrieve_chunks(question, chunks, embeddings, index, top_k=2):
    """
    Retrieves top_k most relevant chunks from FAISS index.
    """
    # We ignore embeddings param because FAISS handles it internally
    model = SentenceTransformer('all-MiniLM-L6-v2')

    query_vector = model.encode([question])
    distances, indices = index.search(query_vector, top_k)

    retrieved = [chunks[i] for i in indices[0]]
    return retrieved


def answer_question(question, context_chunks):
    """
    Runs QA model on retrieved chunks and returns the best answer.
    """
    best_answer = None
    best_score = 0.0

    for chunk in context_chunks:
        result = qa_pipeline({
            "question": question,
            "context": chunk
        })

        if result["score"] > best_score:
            best_answer = result["answer"]
            best_score = result["score"]

    if best_answer:
        return best_answer
    else:
        return "⚠️ Sorry, I couldn't find a confident answer in the document."
