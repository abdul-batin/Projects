import os  
import logging  
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader  
from langchain.text_splitter import RecursiveCharacterTextSplitter  
from langchain.embeddings import HuggingFaceEmbeddings  
from langchain.vectorstores import Chroma  
from chromadb.config import Settings  
from langchain_chroma import Chroma  
from langchain_huggingface import HuggingFaceEmbeddings 
import chromadb  # HTTP Client for Chroma  
from transformers import AutoTokenizer, AutoModelForCausalLM  
from sentence_transformers import SentenceTransformer  
import torch 
  
# Initialize logger  
logger = logging.getLogger()  
logger.setLevel(logging.INFO)  
  
  
def doc_reader(file_dir):  
    """  
    Reads documents from a directory and splits them into chunks.  
    Supports .txt, .pdf, and .docx formats.  
    """  
    all_chunks = []  
    try:  
        logger.info(f"Number of docs to be read = {len(os.listdir(file_dir))}")  
        for file in os.listdir(file_dir):  
            logger.info(f"Reading file {file} from {file_dir}")  
            ext = os.path.splitext(file)[1].lower()  
            fpath = os.path.join(file_dir, file)  
  
            # Choose appropriate loader based on file extension  
            if ext == '.txt':  
                loader = TextLoader(fpath)  
            elif ext == '.docx':  
                loader = Docx2txtLoader(fpath)  
            elif ext == '.pdf':  
                loader = PyPDFLoader(fpath)  
            else:  
                logger.info(f"Skipping unsupported file: {file}")  
                continue  
  
            # Load and split documents into chunks  
            docs = loader.load()  # List of Document objects  
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)  
            chunks = splitter.split_documents(docs)  # List of Document chunks  
            all_chunks.extend(chunks)  
        return all_chunks  
    except Exception as e:  
        logger.error(f"Error reading documents: {e}")  
        return []  
  
def store_in_chromadb(docs, chroma_host="localhost", chroma_port=8000):  
    """  
    Stores document embeddings in ChromaDB using the HTTP client.  
    ChromaDB must be running as a server (e.g., in Docker).  
    """  
    try:  
        # Connect to ChromaDB server via HTTP client  
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)  
  
        # Initialize embedding model properly  
        embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")  
  
        # Initialize Chroma vector store with the HTTP client  
        vectordb = Chroma(client=client, collection_name="embeddings_collection", embedding_function=embedder)  
  
        # Precompute embeddings for the documents  
        # `embed_documents` expects the text content of the documents  
        embeddings = embedder.embed_documents([doc.page_content for doc in docs])  
  
        # Add documents and embeddings to ChromaDB  
        vectordb.add_documents(documents=docs, embeddings=embeddings)  
  
        logger.info(f"Stored {len(docs)} docs/embeddings to ChromaDB server at {chroma_host}:{chroma_port}")  
        return vectordb  
    except Exception as e:  
        logger.error(f"Unable to store in ChromaDB server: {e}")  
        return None   
  
# Define a function to process a query  
def query_chromadb(query: str, collection_name: str = "embeddings_collection"):  
    """  
    Query the ChromaDB server with a given input query.  
  
    Args:  
        query (str): The query string to search for in the embeddings.  
        collection_name (str): The name of the collection to query.  
  
    Returns:  
        list: A list of results from the ChromaDB server.  
    """  
    # Configure ChromaDB client to connect to the HTTP server  
    chroma_settings = Settings(  
        chroma_api_impl="chromadb.api.fastapi.FastAPI",  # Use FastAPI (HTTP-based)  
        chroma_server_host="localhost",  # Host where ChromaDB server is running  
        chroma_server_http_port="8000"  # Port where ChromaDB server is running  
    )  
  
    # Initialize the embedding function  
    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")  
  
    # Connect to the ChromaDB server  
    vectorstore = Chroma(  
        collection_name=collection_name,  # Replace with your collection name  
        embedding_function=embedding_model,  
        client_settings=chroma_settings  
    )  
  
    # Embed the query to get its vector representation  
    query_embedding = embedding_model.embed_query(query)  
  
    # Perform similarity search  
    results = vectorstore.similarity_search_by_vector(query_embedding, k=5)  
  
    # Return the results  
    return results  
  
def load_model(model_name="gpt2"):  
    """  
    Load the language model (e.g., GPT-2 or Falcon) and tokenizer.  
  
    Args:  
        model_name (str): Name of the pre-trained model to load (default: "gpt2").  
  
    Returns:  
        tuple: A tuple containing the tokenizer and model.  
    """  
    # Load the tokenizer  
    tokenizer = AutoTokenizer.from_pretrained(model_name)  
  
    # Add a padding token if missing  
    if tokenizer.pad_token is None:  
        tokenizer.add_special_tokens({'pad_token': '[PAD]'})  
  
    # Determine the appropriate torch data type (float16 for GPU, float32 for CPU)  
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32  
  
    # Load the model  
    model = AutoModelForCausalLM.from_pretrained(  
        model_name,  
        device_map="auto",  # Automatically map model to available GPUs  
        torch_dtype=torch_dtype  # Use appropriate precision  
    )  
  
    # Resize the model's embedding layer to match the tokenizer vocabulary size  
    model.resize_token_embeddings(len(tokenizer))  
  
    return tokenizer, model  
  
# Load an embedding model for ChromaDB  
# Efficient embedding model  
  
def generate_response_with_model(query: str, vectorstore, tokenizer, model, top_k: int = 5):  
    """  
    Generate a natural language response to a query using a language model and ChromaDB.  
  
    Args:  
        query (str): The user's query in natural language.  
        vectorstore: The ChromaDB vectorstore for document retrieval.  
        tokenizer: The tokenizer for the language model.  
        model: The language model for generating responses.  
        top_k (int): The number of relevant documents to retrieve.  
  
    Returns:  
        str: The generated natural language response.  
    """  
    # Dynamically set the device (GPU if available, otherwise CPU)  
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  
    model.to(device)  

    logger.info(f"Using device: {device}")  # Log the device being used for inference
  
    # Handle basic conversational queries  
    if query.lower() in ["hi", "hello", "how are you?", "hey"]:  
        return "Hello! How can I assist you today?"  
  
    # Step 1: Embed the query to retrieve relevant documents  
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  
    query_embedding = embedding_model.encode(query)  

    logger.info(f"Query embedding shape: {query_embedding.shape} generated")  # Log the shape of the query embedding
  
    # Retrieve relevant documents using vectorstore  
    results = vectorstore.similarity_search_by_vector(query_embedding, k=top_k)  

    logger.info(f"Number of results retrieved: {len(results)}")  # Log the number of results retrieved
  
    # Step 2: Handle case when no relevant documents are found  
    if not results:  
        return "I couldn't find anything relevant in the documents. Can you try rephrasing your query?"  
  
    # Step 3: Extract relevant content from the retrieved documents  
    context = "\n\n".join([  
        f"Source: {doc.metadata.get('source', 'Unknown source')}, Page: {doc.metadata.get('page', 'Unknown page')}\nContent: {doc.page_content.strip()}"  
        for doc in results  
    ])  

    logger.info(f"Context length before truncation: {len(context.split())} tokens")  # Log the context length before truncation
  
    # Truncate the context to fit within the model's token limit  
    max_context_length = 1024 - 150  # Reserve 150 tokens for the query and response  
    context_tokens = tokenizer(  
        context,  
        return_tensors="pt",  
        truncation=True,  
        max_length=max_context_length  
    )["input_ids"]  
  
    # Decode the truncated context back into text  
    truncated_context = tokenizer.decode(context_tokens[0], skip_special_tokens=True)  
  
    # Step 4: Construct the prompt with the truncated context  
    prompt = f"""  
    You are an intelligent assistant. A user asked the following question:  
  
    Query: {query}  
  
    I retrieved the following relevant content from the documents:  
  
    {truncated_context}  
  
    Based on the above content, provide a natural language response to the user's query.  
    """  

    logger.info(f"Prompt length: {len(prompt.split())} tokens")  # Log the length of the prompt
  
    # Step 5: Tokenize the prompt 
    #prompt = "Test prompt say hello" 
    inputs = tokenizer(  
        prompt,  
        return_tensors="pt",  
        max_length=1024,  # Ensure the input is within the model's token limit  
        truncation=True,  # Truncate if the input is too long  
        padding="max_length"  # Pad to the maximum length  
    ).to(device)  # Move inputs to the same device as the model  

    # Inspect input IDs  
    print("Input IDs:", inputs["input_ids"])  
    print("Max token ID in input:", torch.max(inputs["input_ids"]))  
    print("Min token ID in input:", torch.min(inputs["input_ids"]))  
    print("Tokenizer vocab size:", len(tokenizer))  
    print("Attention Mask:", inputs["attention_mask"])  
    
    # Step 6: Generate a response using the language model 
    '''outputs = model.generate(  
        inputs["input_ids"],  
        attention_mask=inputs["attention_mask"],  
        max_new_tokens=150,  
        temperature=0.7,  
        top_p=0.9,  
        do_sample=True,  
        pad_token_id=tokenizer.pad_token_id  # Explicitly set the padding token ID  
    )'''

    outputs = model.generate(  
        inputs["input_ids"],  
        attention_mask=inputs["attention_mask"],  
        max_new_tokens=100,  
        temperature=0.7,  
        top_p=0.9,  
        do_sample=True,  
        pad_token_id=tokenizer.pad_token_id  # Explicitly set the padding token ID  
    )   
    
    # Step 7: Decode the model's output to get the generated text  
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)  
  
    # Return the generated response  
    return response  