# src/domains/crew_state/rules.py
from .schema import CrewStatePatch

def validate_crew_patch(patch: CrewStatePatch):
    """乘员状态校验规则"""
    if patch.total_count is not None:
        if patch.total_count < 0:
            raise ValueError(f"乘员总数不能为负数：{patch.total_count}")

    if patch.members is not None:
        ids = set()
        for m in patch.members:
            if m.member_id in ids:
                raise ValueError(f"重复乘员ID: {m.member_id}")
            ids.add(m.member_id)
