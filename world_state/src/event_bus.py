# src/event_bus.py
from pydantic import BaseModel
from typing import Dict
from src.core.logger import logger
from src.domains.environment_state.service import update_environment_state

# 在EventBus初始化里注册事件映射
handlers = {
    "alert.update": [...],
    "crew.update": [...],
    "equipment.update": [...],
    "environment.update": [update_environment_state] # 新增这一行
}
# ========== 事件信封，payload先用dict，运行时再转成对应模型 ==========
class EventEnvelope(BaseModel):
    """
    事件信封：外部仿真服务推送事件统一外层包装
    """
    event_type: str
    payload: Dict
    source: str


class EventBus:
    @staticmethod
    def handle_event(envelope: EventEnvelope):
        logger.info(f"Received event: type={envelope.event_type}, source={envelope.source}")

        if envelope.event_type == "environment.update":
            # 【函数内局部导入，解决NameError + 循环导入】
            from domains.environment_state.schema import EnvironmentStatePatch
            from src.store import global_store
            patch_data = EnvironmentStatePatch(**envelope.payload)
            global_store.apply_environment_patch(patch_data)
            return {"ok": True, "domain": "environment"}

        # ===== 新增这一段 =====
        elif envelope.event_type == "crew.state.patch":
            from domains.crew_state.schema import CrewStatePatch
            from src.store import global_store
            patch_data = CrewStatePatch(**envelope.payload)
            global_store.apply_crew_patch(patch_data)
            return {"ok": True, "domain": "crew"}

        elif envelope.event_type == "alert.state.patch":
            from domains.alert_state.schema import AlertStatePatch
            from src.store import global_store
            patch_data = AlertStatePatch(**envelope.payload)
            global_store.apply_alert_patch(patch_data)
            return {"ok": True, "domain": "alert"}

        elif envelope.event_type == "equipment.state.patch":
            from domains.equipment_state.schema import EquipmentStatePatch
            from src.store import global_store
            patch_data = EquipmentStatePatch(**envelope.payload)
            global_store.apply_equipment_patch(patch_data)
            return {"ok": True, "domain": "equipment"}

        # 后续新增域在这里添加elif
        # elif envelope.event_type == "crew.state.patch":
        raise ValueError(f"Unsupported event_type: {envelope.event_type}")

event_bus = EventBus()
