# src/domains/crew_state/facade.py
from fastapi import APIRouter, HTTPException
from .schema import CrewState, CrewStatePatch
from .service import apply_crew_patch

router = APIRouter(prefix="/domain/crew", tags=["crew_state"])

class CrewStateAPI:
    @staticmethod
    def apply_patch(current: CrewState, patch: CrewStatePatch) -> CrewState:
        return apply_crew_patch(current, patch)

    @staticmethod
    def get_empty_state() -> CrewState:
        return CrewState()


# ========== HTTP接口定义 ==========
@router.get("/state", response_model=CrewState)
def get_crew_state():
    """读取乘员域当前状态（调试接口）"""
    from src.store import global_store
    return global_store.crew

@router.patch("/state", response_model=CrewState)
def patch_crew_state(patch: CrewStatePatch):
    """增量更新乘员状态"""
    try:
        from src.store import global_store
        global_store.apply_crew_patch(patch)
        return global_store.crew
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/state", response_model=CrewState)
def put_crew_state(new_full_state: CrewState):
    """全量覆盖乘员状态"""
    try:
        from src.store import global_store
        full_patch = CrewStatePatch(**new_full_state.model_dump())
        global_store.apply_crew_patch(full_patch)
        return global_store.crew
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/state", response_model=CrewState)
def reset_crew_state():
    """重置乘员状态为空"""
    empty_state = CrewStateAPI.get_empty_state()
    full_patch = CrewStatePatch(**empty_state.model_dump())
    from src.store import global_store
    global_store.apply_crew_patch(full_patch)
    return global_store.crew
