from typing import Dict, Any, List
from structlog import get_logger
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from core.llm_client import AsyncGeminiClient
from langchain_core.messages import SystemMessage, HumanMessage
import json

logger = get_logger(__name__)

class SupervisorAgent:
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.llm = AsyncGeminiClient(temperature=0.0)
        
    async def _decompose_query(self, user_query: str) -> List[str]:
        """Decomposes the user query into specific search queries."""
        sys_msg = SystemMessage(content=(
            "You are a search strategist. Given a user's market research query, "
            "generate 3 specific, distinct search queries to gather comprehensive data. "
            "IMPORTANT: Use natural language only. DO NOT use quotes (\"), boolean operators (AND/OR), "
            "or complex search syntax, as they break the search engine. "
            "Return ONLY a JSON array of strings. No markdown formatting."
        ))
        hum_msg = HumanMessage(content=user_query)
        
        res = await self.llm.ainvoke([sys_msg, hum_msg])
        content = res.content.strip()
        if content.startswith("```json"): content = content[7:-3].strip()
        elif content.startswith("```"): content = content[3:-3].strip()
            
        try:
            return json.loads(content)
        except Exception as e:
            logger.error("decompose_failed", error=str(e), content=content)
            # Fallback to the original query if parsing fails
            return [user_query]

    async def execute(self, user_query: str) -> Dict[str, Any]:
        """Orchestrates the market research workflow."""
        logger.info("supervisor_starting", query=user_query)
        
        # 1. Decompose Query
        search_queries = await self._decompose_query(user_query)
        logger.info("generated_queries", queries=search_queries)
        
        # 2. Research
        raw_facts = await self.researcher.execute(search_queries, research_goal=user_query)
        
        # 3. Analyze & Format
        final_report = await self.analyst.execute(raw_facts, user_query)
        
        logger.info("workflow_complete")
        return final_report