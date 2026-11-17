# src/domains/alert_state/schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import StrEnum

class AlertLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertItem(BaseModel):
    alert_id: str
    title: str
    level: AlertLevel
    source: str
    is_resolved: bool = False

class AlertState(BaseModel):
    alerts: List[AlertItem] = Field(default_factory=list, description="当前激活告警列表")

class AlertStatePatch(BaseModel):
    alerts: Optional[List[AlertItem]] = None
