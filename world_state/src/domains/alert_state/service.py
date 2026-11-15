# src/domains/alert_state/service.py
from copy import deepcopy
from .schema import AlertState, AlertStatePatch
from .rules import validate_alert_patch

def apply_alert_patch(current: AlertState, patch: AlertStatePatch) -> AlertState:
    validate_alert_patch(patch)
    new_state = deepcopy(current)
    if patch.alerts is not None:
        new_state.alerts = patch.alerts
    return new_state
