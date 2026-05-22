# doc_indexer.py
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Load embedding model once
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyMuPDF, fallback to OCR if image-based."""
    doc = fitz.open(file_path)
    text = []
    for page in doc:
        page_text = page.get_text("text")
        if page_text.strip():
            text.append(page_text)
        else:
            # OCR fallback
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img)
            text.append(page_text)
    return "\n".join(text)

def chunk_text(text, chunk_size=500, overlap=100):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks

def build_faiss_index(chunks):
    """Build FAISS index from text chunks."""
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index, embeddings
