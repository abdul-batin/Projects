import os
import logging
import chromadb
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def doc_reader(file_dir):
    all_chunks = []
    try:
        logger.info(f"Number of docs to be read = {len(os.listdir(file_dir))}")
        for file in os.listdir(file_dir):
            logger.info(f"Reading file {file} from {file_dir}")

            ext = os.path.splitext(file)[1].lower()
            fpath = os.path.join(file_dir, file)

            if ext == '.txt':
                loader = TextLoader(fpath)
            elif ext == '.docx':
                loader = Docx2txtLoader(fpath)
            elif ext == '.pdf':
                loader = PyPDFLoader(fpath)
            else:
                logger.info(f"Skipping unsupported file: {file}")
                continue

            docs = loader.load()  # List of Document objects
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunks = splitter.split_documents(docs)  # List of Document chunks
            all_chunks.extend(chunks)
        return all_chunks
    except Exception as e:
        logger.info(f"Error reading document: {e}")
        return []

def store_in_chromadb(docs, chroma_host="localhost", chroma_port=8000):
    """
    docs: List of langchain_core.documents.Document objects
    """
    try:
        # Connect to running Chroma server
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

        # Initialize LangChain Chroma vectorstore with remote client
        vectordb = Chroma(client=client, collection_name="default_collection")

        # IMPORTANT: Pass embedding function during add_documents
        vectordb.add_documents(docs, embedding=embedder)

        logger.info(f"Stored {len(docs)} docs/embeddings to ChromaDB server at {chroma_host}:{chroma_port}")
        return vectordb

    except Exception as e:
        logger.info(f"Unable to store in chromadb server: {e}")
        return None

