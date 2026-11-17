# src/domains/equipment_state/schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import StrEnum

class EquipmentStatus(StrEnum):
    NORMAL = "normal"
    WARNING = "warning"
    FAULT = "fault"
    OFFLINE = "offline"

class EquipmentItem(BaseModel):
    equip_id: str
    name: str
    category: str
    status: EquipmentStatus = EquipmentStatus.NORMAL
    power: float = Field(ge=0, le=100, description="功率占比 0~100")

class EquipmentState(BaseModel):
    devices: List[EquipmentItem] = Field(default_factory=list, description="全部设备列表")

class EquipmentStatePatch(BaseModel):
    devices: Optional[List[EquipmentItem]] = None
