# src/domains/equipment_state/facade.py
from fastapi import APIRouter, HTTPException
from .schema import EquipmentState, EquipmentStatePatch
from .service import apply_equipment_patch

router = APIRouter(prefix="/domain/equipment", tags=["equipment_state"])

class EquipmentStateAPI:
    @staticmethod
    def apply_patch(current: EquipmentState, patch: EquipmentStatePatch) -> EquipmentState:
        return apply_equipment_patch(current, patch)

    @staticmethod
    def get_empty_state() -> EquipmentState:
        return EquipmentState()


@router.get("/state", response_model=EquipmentState)
def get_equipment_state():
    """读取设备域状态（调试接口）"""
    from src.store import global_store
    return global_store.equipment

@router.patch("/state", response_model=EquipmentState)
def patch_equipment_state(patch: EquipmentStatePatch):
    """增量更新设备状态"""
    try:
        from src.store import global_store
        global_store.apply_equipment_patch(patch)
        return global_store.equipment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/state", response_model=EquipmentState)
def put_equipment_state(new_full_state: EquipmentState):
    """全量覆盖设备状态"""
    try:
        from src.store import global_store
        full_patch = EquipmentStatePatch(**new_full_state.model_dump())
        global_store.apply_equipment_patch(full_patch)
        return global_store.equipment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/state", response_model=EquipmentState)
def reset_equipment_state():
    """清空设备列表"""
    empty_state = EquipmentStateAPI.get_empty_state()
    full_patch = EquipmentStatePatch(**empty_state.model_dump())
    from src.store import global_store
    global_store.apply_equipment_patch(full_patch)
    return global_store.equipment
