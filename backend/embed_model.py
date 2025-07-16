
from openai import AzureOpenAI

import os
class AzureEmbedder:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_EMBEDDING_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        self.model = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

    def embed_query(self, text: str) -> list[float]:
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return []
        
    def embed_batch(self, texts: list[str]):
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]    
