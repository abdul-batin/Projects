from utils.utils import doc_reader,store_in_chromadb
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
    cnt=0
    while cnt<10:
        logger.info(cnt+2)
        cnt+=1

if __name__ == "__main__":
    main()