from backend.vectordb import get_azure_ai_search
from openai import AzureOpenAI
import os
from azure.search.documents.models import VectorizedQuery
from backend.logger import setup_logger

logger = setup_logger()

def search_query(user_query):
    try:
        #  Embed the query using Azure OpenAI embedding model
        client_embed = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_EMBEDDING_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        embedding_response = client_embed.embeddings.create(
            input=user_query,
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        )
        query_vector = embedding_response.data[0].embedding

        
        client_search = get_azure_ai_search()

        # Create a VectorizedQuery for vector search
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=3,
            fields="content_vector"
        )



        results = client_search.search(
            search_text="",  # empty because we re doing pure vector search
            vector_queries=[vector_query],

            
            
            select=["content"]
        )
        logger.info("Similarity search done successfully.")
        top_chunks = "\n\n".join([doc["content"] for doc in results])

        # Step 3: Call GPT with retrieved context
        client_chat = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        response = client_chat.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a helpful document assistant. Answer the user's question based on the provided context."},
                {"role": "user", "content": f"Answer based on the following context:\n\n{top_chunks}\n\nQuestion: {user_query}"}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return "Search error occurred. Try again."
