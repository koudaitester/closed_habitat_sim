# src/domains/alert_state/facade.py
from fastapi import APIRouter, HTTPException
from .schema import AlertState, AlertStatePatch
from .service import apply_alert_patch

router = APIRouter(prefix="/domain/alert", tags=["alert_state"])

class AlertStateAPI:
    @staticmethod
    def apply_patch(current: AlertState, patch: AlertStatePatch) -> AlertState:
        return apply_alert_patch(current, patch)

    @staticmethod
    def get_empty_state() -> AlertState:
        return AlertState()


@router.get("/state", response_model=AlertState)
def get_alert_state():
    """读取告警域状态（调试接口）"""
    from src.store import global_store
    return global_store.alert

@router.patch("/state", response_model=AlertState)
def patch_alert_state(patch: AlertStatePatch):
    """增量更新告警状态"""
    try:
        from src.store import global_store
        global_store.apply_alert_patch(patch)
        return global_store.alert
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/state", response_model=AlertState)
def put_alert_state(new_full_state: AlertState):
    """全量覆盖告警状态"""
    try:
        from src.store import global_store
        full_patch = AlertStatePatch(**new_full_state.model_dump())
        global_store.apply_alert_patch(full_patch)
        return global_store.alert
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/state", response_model=AlertState)
def reset_alert_state():
    """清空所有告警"""
    empty_state = AlertStateAPI.get_empty_state()
    full_patch = AlertStatePatch(**empty_state.model_dump())
    from src.store import global_store
    global_store.apply_alert_patch(full_patch)
    return global_store.alert
