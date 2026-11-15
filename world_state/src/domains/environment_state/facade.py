# src/domains/environment_state/facade.py
from fastapi import APIRouter, HTTPException
from .schema import EnvironmentState, EnvironmentStatePatch
from .service import apply_environment_patch

router = APIRouter(prefix="/domain/environment", tags=["environment_state"])

class EnvironmentStateAPI:
    @staticmethod
    def apply_patch(current: EnvironmentState, patch: EnvironmentStatePatch) -> EnvironmentState:
        return apply_environment_patch(current, patch)

    @staticmethod
    def get_empty_state() -> EnvironmentState:
        return EnvironmentState()


# ========== HTTP接口定义 ==========
@router.get("/state", response_model=EnvironmentState)
def get_environment_state():
    """【Read】读取当前环境分片状态"""
    from src.store import global_store  # ✅ 移到函数内部导入，打破循环
    return global_store.environment

@router.patch("/state", response_model=EnvironmentState)
def patch_environment_state(patch: EnvironmentStatePatch):
    """【Update】增量更新环境状态"""
    try:
        from src.store import global_store # ✅ 函数内导入
        global_store.apply_environment_patch(patch)
        return global_store.environment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/state", response_model=EnvironmentState)
def put_environment_state(new_full_state: EnvironmentState):
    """【Full Replace】全量覆盖环境状态"""
    try:
        from src.store import global_store # ✅ 函数内导入
        full_patch = EnvironmentStatePatch(**new_full_state.model_dump())
        global_store.apply_environment_patch(full_patch)
        return global_store.environment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/state", response_model=EnvironmentState)
def reset_environment_state():
    """【Reset】重置环境状态为空初始状态"""
    empty_state = EnvironmentStateAPI.get_empty_state()
    full_patch = EnvironmentStatePatch(**empty_state.model_dump())
    from src.store import global_store # ✅ 函数内导入
    global_store.apply_environment_patch(full_patch)
    return global_store.environment
