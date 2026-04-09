from pydantic import BaseModel, ConfigDict, Field


class TopSkuItem(BaseModel):
    sku: str
    revenue: float = Field(ge=0)


class WindowReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revenue: float = Field(ge=0)
    orders_count: int = Field(ge=0)
    margin: float = Field(ge=0)
    top_sku: list[TopSkuItem]


class FullReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: WindowReport
    week: WindowReport
