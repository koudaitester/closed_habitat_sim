from src.client.worldstate_client import WorldStateClient
from src.core.logger import logger


ws_client = WorldStateClient()

async def inject_equipment_fault(device_id: str, is_fault: bool):
    """注入设备故障，推送 equipment.state.patch"""
    event = {
        "type": "equipment.state.patch",
        "source": "fault_injector",
        "payload": {
            "devices": [
                {
                    "equip_id": device_id,
                    "fault": is_fault,
                    "name": "O2 Generator",
                    "category": "life_support",
                    "power": True
                }
            ]
        }
    }
    return await ws_client.submit_event(event)

async def inject_alert(alert_msg: str):
    """注入告警事件 alert.state.patch"""
    event = {
        "type": "alert.state.patch",
        "source": "fault_injector",
        "payload": {
            "message": alert_msg,
            "active": True
        }
    }
    return await ws_client.submit_event(event)
