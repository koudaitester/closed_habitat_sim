# src/domains/crew_state/service.py
from copy import deepcopy
from .schema import CrewState, CrewStatePatch
from .rules import validate_crew_patch

def apply_crew_patch(current: CrewState, patch: CrewStatePatch) -> CrewState:
    """
    合并增量patch到当前乘员状态
    """
    # 先校验
    validate_crew_patch(patch)
    new_state = deepcopy(current)

    # 有就覆盖，None则保留原值
    if patch.total_count is not None:
        new_state.total_count = patch.total_count

    if patch.members is not None:
        new_state.members = patch.members

    return new_state
