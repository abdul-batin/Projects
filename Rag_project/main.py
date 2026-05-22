from utils.utils import doc_reader,store_in_chromadb,query_chromadb,generate_response_with_model,load_model
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="logs/chatbot.log",
    filemode="w", 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def main():

    file_dir = "documents"

    contents = doc_reader(file_dir=file_dir)
    #logger.info(contents)
    vector_store = store_in_chromadb(contents)
    query = "What to do if i cut my wrist by mistake?"
    response = query_chromadb(query=query)
    tokenizer, model = load_model()  
    logger.info("Model loaded successfully. Generating response...")
    # Check tokenizer vocab size  
    print(f"Tokenizer vocab size: {len(tokenizer)}")  
    
    # Check model vocab size  
    print(f"Model embedding size: {model.config.vocab_size}")  
    query_response = generate_response_with_model(query=query,vectorstore=vector_store, tokenizer=tokenizer, model=model)

    logger.info(vector_store)
    logger.info(response)
    logger.info(query_response)

if __name__ == "__main__":
    main()