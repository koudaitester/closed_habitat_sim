# src/domains/alert_state/rules.py
from .schema import AlertStatePatch

def validate_alert_patch(patch: AlertStatePatch):
    if patch.alerts is not None:
        alert_ids = set()
        for alert in patch.alerts:
            if alert.alert_id in alert_ids:
                raise ValueError(f"告警ID重复: {alert.alert_id}")
            alert_ids.add(alert.alert_id)
