# src/domains/equipment_state/rules.py
from .schema import EquipmentStatePatch

def validate_equipment_patch(patch: EquipmentStatePatch):
    if patch.devices is not None:
        equip_ids = set()
        for dev in patch.devices:
            if dev.equip_id in equip_ids:
                raise ValueError(f"设备ID重复: {dev.equip_id}")
            equip_ids.add(dev.equip_id)
