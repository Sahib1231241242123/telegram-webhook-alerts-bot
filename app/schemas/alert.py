from pydantic import BaseModel, ConfigDict, Field


class AlertRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=500)
    severity: str = Field(min_length=1, max_length=20)
    status: str = Field(min_length=1, max_length=20)
    reasoning: str = Field(min_length=1)
    expected_impact: str = Field(min_length=1)
