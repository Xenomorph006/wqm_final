from typing import List

from pydantic import BaseModel, Field


class WaterObservation(BaseModel):

    ph: float = Field(...)

    turbidity: float = Field(...)

    temperature: float = Field(...)

    dissolved_oxygen: float = Field(...)

    tds: float = Field(...)


class WaterObservationBatch(BaseModel):

    observations: List[WaterObservation]


class HealthResponse(BaseModel):

    status: str

    agent_ready: bool