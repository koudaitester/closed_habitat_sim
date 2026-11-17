# src/domains/environment_state/service.py
from .schema import EnvironmentState, EnvironmentStatePatch
from .rules import validate_environment_patch
from src.core.logger import logger

def apply_environment_patch(
    current_state: EnvironmentState,
    patch: EnvironmentStatePatch
) -> EnvironmentState:
    """
    应用增量补丁
    1. 执行规则校验
    2. 合并更新字段，返回新状态实例
    """
    validate_environment_patch(patch)
    update_data = patch.model_dump(exclude_unset=True)
    new_state = current_state.model_copy(update=update_data)
    return new_state

async def update_environment_state(payload: dict):
    from src.store import global_store

    """接收environment.update事件，更新全局store内环境状态"""
    env_state = global_store.environment
    # 增量更新，只覆盖传过来的字段
    if "temperature" in payload:
        env_state.temperature = payload["temperature"]
    if "co2_ppm" in payload:
        env_state.co2_ppm = payload["co2_ppm"]
    # 版本号自增
    global_store.version += 1
    logger.info(f"环境状态已更新：{env_state}")