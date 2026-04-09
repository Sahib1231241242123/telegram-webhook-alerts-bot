from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(min_length=1)
    sku: str = Field(min_length=1, max_length=120)
    revenue: float = Field(ge=0)
    margin: float = Field(ge=0)
    created_at: datetime
