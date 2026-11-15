# src/domains/environment_state/service.py
from .schema import EnvironmentState, EnvironmentStatePatch
from .rules import validate_environment_patch

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
