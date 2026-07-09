import json
from structlog import get_logger
from langchain_core.messages import SystemMessage, HumanMessage
from core.llm_client import AsyncGeminiClient

logger = get_logger(__name__)

class AnalystAgent:
    def __init__(self, model: str = "gemini-2.5-flash", api_key: str = None):
        self.llm = AsyncGeminiClient(model_name=model, temperature=0.2, api_key=api_key)
        with open("agents/prompts/market_research.txt", "r") as f:
            self.system_prompt = f.read()
            
    async def execute(self, raw_facts: str, user_query: str) -> dict:
        """
        Takes raw factual data and the original user query, and returns a structured MarketReport.
        """
        logger.info("analyst_starting")
        
        sys_msg = SystemMessage(content=self.system_prompt)
        hum_msg = HumanMessage(content=(
            f"User Query: {user_query}\n\n"
            f"Raw Research Facts:\n{raw_facts}\n\n"
            "Format your response EXACTLY as a valid JSON object matching this schema:\n"
            "{\n"
            "  \"title\": \"string\",\n"
            "  \"executive_summary\": \"string\",\n"
            "  \"key_trends\": [{\"trend_name\": \"string\", \"adoption_level\": \"string\", \"description\": \"string\", \"asi_relevance\": \"string\"}],\n"
            "  \"quantitative_data\": [{\"metric_name\": \"string\", \"value\": \"string\", \"context\": \"string\", \"source\": \"string\"}],\n"
            "  \"strategic_recommendations\": [\"string\"]\n"
            "}\n"
            "Do not include markdown code blocks like ```json."
        ))
        
        response = await self.llm.ainvoke([sys_msg, hum_msg])
        content = response.content.strip()
        
        # Clean up possible markdown code blocks if the model ignores the prompt
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("json_parse_failed", error=str(e), content=content)
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")