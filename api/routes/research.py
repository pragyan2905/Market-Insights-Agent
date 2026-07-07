from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.supervisor import SupervisorAgent
from guardrails.output_parser import MarketReport
import traceback

router = APIRouter(prefix="/api/v1/research", tags=["Research"])

class ResearchRequest(BaseModel):
    query: str

@router.post("/", response_model=MarketReport)
async def generate_research_report(request: ResearchRequest):
    try:
        supervisor = SupervisorAgent()
        report_data = await supervisor.execute(request.query)
        # Validate through Pydantic
        report = MarketReport(**report_data)
        return report
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
