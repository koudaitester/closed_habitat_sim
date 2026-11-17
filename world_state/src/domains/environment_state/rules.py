# src/domains/environment_state/rules.py
from .schema import EnvironmentStatePatch

def validate_environment_patch(patch: EnvironmentStatePatch) -> None:
    """环境分片数据校验规则，非法值抛出ValueError"""
    if patch.temperature is not None:
        if not (-20.0 <= patch.temperature <= 80.0):
            raise ValueError(f"温度 {patch.temperature}℃ 超出合法范围 [-20,80]")

    if patch.humidity is not None:
        if not (0.0 <= patch.humidity <= 100.0):
            raise ValueError(f"湿度 {patch.humidity}% 超出合法范围 [0,100]")

    if patch.co2_ppm is not None:
        if patch.co2_ppm < 0:
            raise ValueError(f"CO₂浓度不能为负数：{patch.co2_ppm}")

    if patch.vapor_pressure is not None:
        if patch.vapor_pressure < 0:
            raise ValueError(f"水汽分压不能为负数：{patch.vapor_pressure}")
