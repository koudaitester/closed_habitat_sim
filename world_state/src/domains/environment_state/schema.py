# src/domains/environment_state/schema.py
from pydantic import BaseModel
from typing import Optional

class EnvironmentState(BaseModel):
    """舱内环境完整持久化状态"""
    temperature: Optional[float] = None      # 温度 ℃
    humidity: Optional[float] = None         # 相对湿度 %
    co2_ppm: Optional[float] = None          # 二氧化碳浓度 ppm
    vapor_pressure: Optional[float] = None   # 水汽分压 kPa

class EnvironmentStatePatch(BaseModel):
    """增量补丁，外部服务提交事件时只传变化字段"""
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2_ppm: Optional[float] = None
    vapor_pressure: Optional[float] = None
