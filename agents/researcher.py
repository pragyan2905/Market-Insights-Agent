import asyncio
from typing import List, Dict, Any
from ddgs import DDGS
import trafilatura
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from structlog import get_logger

from core.memory import DynamicWebRAG
from core.llm_client import AsyncGeminiClient
from langchain_core.messages import SystemMessage, HumanMessage

logger = get_logger(__name__)

class ResearcherAgent:
    def __init__(self, model: str = "gemini-2.5-flash", api_key: str = None):
        self.rag = DynamicWebRAG(api_key=api_key)
        self.llm = AsyncGeminiClient(model_name=model, temperature=0.1, api_key=api_key) # low temp for facts
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
    async def _search_and_scrape(self, queries: List[str], max_results_per_query: int = 3) -> List[Document]:
        """Searches DDG and scrapes the URLs."""
        urls = set()
        for query in queries:
            try:
                results = DDGS().text(query, max_results=max_results_per_query)
                for r in results:
                    urls.add(r.get('href'))
            except Exception as e:
                logger.error("ddg_search_failed", query=query, error=str(e))
                
        logger.info("urls_found", count=len(urls))
        
        documents = []
        for url in urls:
            try:
                downloaded = trafilatura.fetch_url(url)
                if downloaded:
                    text = trafilatura.extract(downloaded, include_tables=True, include_comments=False)
                    if text:
                        documents.append(Document(page_content=text, metadata={"source": url}))
            except Exception as e:
                logger.warning("scraping_failed", url=url, error=str(e))
                
        # Split documents and enforce hard limit for Free Tier API Quota
        docs = self.text_splitter.split_documents(documents)
        return docs[:90]

    async def execute(self, queries: List[str], research_goal: str) -> str:
        """
        Executes the Web-RAG pipeline and returns a factual summary.
        """
        logger.info("researcher_starting", queries=queries)
        
        docs = await self._search_and_scrape(queries)
        if not docs:
            return "No data found for the given queries."
            
        collection_name = await self.rag.create_session_collection()
        
        try:
            await self.rag.index_documents(collection_name, docs)
            
            # Retrieve for the main research goal
            retrieved = await self.rag.retrieve(collection_name, research_goal, top_k=10)
            
            # Format retrieved contexts
            contexts = []
            for item in retrieved:
                source = item["metadata"].get("source", "Unknown")
                contexts.append(f"Source: {source}\nContent: {item['text']}")
                
            combined_context = "\n\n---\n\n".join(contexts)
            
            # Use LLM to extract facts
            sys_msg = SystemMessage(content=(
                "You are a Research Assistant. Extract factual bullet points, metrics, "
                "and key trends from the provided context relevant to the user's research goal. "
                "Include the source URLs for any metrics. Be concise and eliminate filler."
            ))
            hum_msg = HumanMessage(content=f"Research Goal: {research_goal}\n\nContext:\n{combined_context}")
            
            response = await self.llm.ainvoke([sys_msg, hum_msg])
            return response.content
        finally:
            await self.rag.cleanup_collection(collection_name)