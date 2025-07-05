from backend.vectordb import get_azure_ai_search
from langchain.chat_models import AzureChatOpenAI
import os
from backend.logger import setup_logger
from dotenv import load_dotenv
load_dotenv()
logger = setup_logger()

def search_query(user_query):
    try:
        client = get_azure_ai_search()
        results = client.search(search_text=user_query,
                                vectors=[{
                                    "value": None,
                                    "fields": "content_vector",
                                    "k": 3
                                }],
                                select=["content"])

        top_chunks = "\n\n".join([doc["content"] for doc in results])
        llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),      
)

        prompt = f"You are a document assistant, provide to the point answer to the user with simple,clear words for better understanding
        Answer based on the following context:\n\n {top_chunks} \n\nQuestion: {user_query}"
        answer = llm.invoke(prompt)
        return answer.content
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return "Search error occurred. Try again."
