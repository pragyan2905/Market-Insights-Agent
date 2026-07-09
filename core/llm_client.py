import os
from typing import Any, Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from pydantic import SecretStr
from structlog import get_logger

logger = get_logger(__name__)

class AsyncGeminiClient:
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.0, api_key: Optional[str] = None):
        self.model_name = model_name
        
        # Use provided key, otherwise fallback to env
        resolved_api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not resolved_api_key:
            logger.warning("GOOGLE_API_KEY environment variable is not set. LLM calls will fail.")
            
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=temperature,
            api_key=SecretStr(resolved_api_key) if resolved_api_key else None,
            convert_system_message_to_human=True,
        )

    async def ainvoke(self, messages: List[BaseMessage], **kwargs) -> Any:
        """
        Asynchronously invoke the Gemini model with a list of messages.
        """
        logger.info("invoking_gemini", model=self.model_name, message_count=len(messages))
        try:
            response = await self.llm.ainvoke(messages, **kwargs)
            # Log token usage if available in the response metadata
            if hasattr(response, "response_metadata") and response.response_metadata:
                token_usage = response.response_metadata.get("token_usage", {})
                if token_usage:
                    logger.info("gemini_token_usage", token_usage=token_usage)
            return response
        except Exception as e:
            logger.error("gemini_invocation_failed", error=str(e))
            raise