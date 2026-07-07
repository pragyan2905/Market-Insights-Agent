from pydantic import BaseModel, Field
from typing import List

class QuantitativeMetric(BaseModel):
    metric_name: str = Field(description="The name of the metric (e.g., 'Cost Reduction', 'Throughput')")
    value: str = Field(description="The quantitative value, including units (e.g., '15%', '$2M')")
    context: str = Field(description="Brief context explaining what this metric represents")
    source: str = Field(description="The URL or entity where this metric was sourced")

class QualitativeTrend(BaseModel):
    trend_name: str = Field(description="A concise name for the trend")
    description: str = Field(description="A detailed description of the trend and its industry impact")
    adoption_level: str = Field(description="Current level of adoption (e.g., 'Early Stage', 'Mainstream')")
    asi_relevance: str = Field(description="How this trend relates to AGI/ASI workflows or future AI capabilities")

class MarketReport(BaseModel):
    title: str = Field(description="The title of the market research report")
    executive_summary: str = Field(description="A high-level summary of the findings")
    key_trends: List[QualitativeTrend] = Field(description="List of identified qualitative trends")
    quantitative_data: List[QuantitativeMetric] = Field(description="List of quantitative data points extracted")
    strategic_recommendations: List[str] = Field(description="Actionable recommendations based on the data")