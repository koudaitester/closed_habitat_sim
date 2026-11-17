from pydantic import BaseModel

class EnvPhysicalInput(BaseModel):
    temperature: float
    oxygen: float
    co2: float
    pressure: float
    crew_count: int
    equipment_state: dict

class EnvPhysicalResult(BaseModel):
    temperature: float
    oxygen: float
    co2: float
    pressure: float
    event_type: str = "environment.update"
