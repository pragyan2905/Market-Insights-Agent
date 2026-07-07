from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.supervisor import SupervisorAgent
from guardrails.output_parser import MarketReport
import traceback

router = APIRouter(prefix="/api/v1/research", tags=["Research"])

from typing import Optional

class ResearchRequest(BaseModel):
    query: str
    api_key: Optional[str] = None
    model: Optional[str] = "gemini-3.0-pro"

@router.post("/", response_model=MarketReport)
async def generate_research_report(request: ResearchRequest):
    try:
        supervisor = SupervisorAgent(model=request.model, api_key=request.api_key)
        report_data = await supervisor.execute(request.query)
        # Validate through Pydantic
        report = MarketReport(**report_data)
        return report
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
