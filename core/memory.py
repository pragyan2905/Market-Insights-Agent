import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from structlog import get_logger

logger = get_logger(__name__)

import os

class DynamicWebRAG:
    """
    Manages an in-memory Qdrant instance for dynamic Web-RAG.
    Creates temporary collections for specific research sessions.
    """
    def __init__(self, embedding_model: str = "models/gemini-embedding-001", api_key: Optional[str] = None):
        # We use an in-memory instance for fast, temporary Web-RAG collections
        self.client = AsyncQdrantClient(location=":memory:")
        
        resolved_api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=resolved_api_key
        )
        # Vector size for gemini-embedding-001 is 3072
        self.vector_size = 3072 

    async def create_session_collection(self) -> str:
        """Creates a unique temporary collection for a research session."""
        collection_name = f"research_session_{uuid.uuid4().hex}"
        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
        )
        logger.info("created_rag_collection", collection_name=collection_name)
        return collection_name

    async def index_documents(self, collection_name: str, documents: List[Document]) -> int:
        """Embeds and indexes documents into the specified collection."""
        if not documents:
            return 0
            
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        logger.info("embedding_documents", count=len(texts), collection=collection_name)
        
        vectors = await self.embeddings.aembed_documents(texts)
        
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": text, **metadata}
            )
            for vector, text, metadata in zip(vectors, texts, metadatas)
        ]
        
        await self.client.upsert(
            collection_name=collection_name,
            points=points
        )
        logger.info("indexed_documents", count=len(points), collection=collection_name)
        return len(points)

    async def retrieve(self, collection_name: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieves top-k most relevant chunks for the query."""
        logger.info("retrieving_documents", query=query, top_k=top_k, collection=collection_name)
        query_vector = await self.embeddings.aembed_query(query)
        
        results = await self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=top_k
        )
        
        retrieved = []
        for res in results.points:
            retrieved.append({
                "score": res.score,
                "text": res.payload.get("text", ""),
                "metadata": {k: v for k, v in res.payload.items() if k != "text"}
            })
            
        logger.info("retrieved_documents", count=len(retrieved))
        return retrieved

    async def cleanup_collection(self, collection_name: str):
        """Deletes the temporary collection."""
        await self.client.delete_collection(collection_name=collection_name)
        logger.info("deleted_rag_collection", collection_name=collection_name)