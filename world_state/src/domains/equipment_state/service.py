# src/domains/equipment_state/service.py
from copy import deepcopy
from .schema import EquipmentState, EquipmentStatePatch
from .rules import validate_equipment_patch

def apply_equipment_patch(current: EquipmentState, patch: EquipmentStatePatch) -> EquipmentState:
    validate_equipment_patch(patch)
    new_state = deepcopy(current)
    if patch.devices is not None:
        new_state.devices = patch.devices
    return new_state
