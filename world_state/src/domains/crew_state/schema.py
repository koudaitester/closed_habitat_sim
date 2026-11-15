# src/domains/crew_state/schema.py
from pydantic import BaseModel, Field
from typing import List, Optional

class CrewMember(BaseModel):
    member_id: str
    name: str
    health: float = Field(ge=0, le=100, description="健康值 0~100")
    fatigue: float = Field(ge=0, le=100, description="疲劳度 0~100")
    emotion: float = Field(ge=0, le=100, description="情绪 0~100")
    task_id: Optional[str] = None

class CrewState(BaseModel):
    members: List[CrewMember] = Field(default_factory=list, description="全部乘员列表")
    total_count: int = 0

class CrewStatePatch(BaseModel):
    """增量更新patch，所有字段都是可选"""
    members: Optional[List[CrewMember]] = None
    total_count: Optional[int] = None
