# AbdulBatin_AI_Agent_Challenge - Document Analyzer

## What it does
A small web application that lets users upload PDF documents and ask natural language questions about their contents. It extracts text, creates embeddings, stores them in a vector index, and performs retrieval-augmented generation using a modern LLM.

## Key features
- Upload PDF files (single or batch).
- Robust text extraction (PyMuPDF), with optional OCR fallback.
- Chunking + embeddings + FAISS vector store for retrieval.
- Conversational Q&A and document summarization via LLM.
- Downloadable summary / Q&A.

## Limitations
- Quality depends on the OCR and LLM model used.
- Not optimized for very large corpora or multi-user production workloads.
- Uses external APIs (OpenAI) — watch cost and data sensitivity.

## Tech stack & APIs used
- Python 3.12
- Streamlit (UI)
- PyMuPDF (text extraction)
- OpenAI API (embeddings + LLM)
- FAISS (vector store)
- tiktoken (tokenization)
- Optional: pytesseract for OCR

## Setup (local)
1. Clone this folder.
2. Create and activate virtual environment(python3.12)
3. Install requirements/requirements.txt
4. 
