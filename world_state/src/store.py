# src/store.py
from copy import deepcopy
from datetime import datetime
from typing import Dict, Optional
from domains.environment_state import EnvironmentState, EnvironmentStateAPI
from domains.environment_state.schema import EnvironmentStatePatch
from domains.crew_state import CrewState, CrewStateAPI
from domains.crew_state.schema import CrewStatePatch
from domains.alert_state import AlertState, AlertStateAPI
from domains.alert_state.schema import AlertStatePatch
from domains.equipment_state import EquipmentState, EquipmentStateAPI
from domains.equipment_state.schema import EquipmentStatePatch
from core.logger import logger
from core.config import settings

class WorldStateStore:
    def __init__(self):
        self.environment: EnvironmentState = EnvironmentStateAPI.get_empty_state()
        self.crew: CrewState = CrewStateAPI.get_empty_state()

        self.alert: AlertState = AlertStateAPI.get_empty_state()
        self.equipment: EquipmentState = EquipmentStateAPI.get_empty_state()

        self.version: int = 0
        # ==========新增仿真时钟状态==========
        self.sim_time_day: int = 1       # 任务第几天
        self.sim_time_h: int = 0
        self.sim_time_m: int = 0
        self.sim_time_s: int = 0
        self.sim_paused: bool = True     # 默认暂停，拍戏方便
        self.sim_speed: float = 1.0     # 倍速：0.5 /1 /2 /5

        self.last_modified: Optional[datetime] = None
        self.snapshots: Dict[int, "WorldStateStore.SnapshotRecord"] = {}

    class SnapshotRecord:
        def __init__(self, version: int, ts: datetime,
                     env: EnvironmentState,
                     crew: CrewState,
                     alert: AlertState,
                     equip: EquipmentState):
            self.version = version
            self.ts = ts
            self.environment = deepcopy(env)
            self.crew = deepcopy(crew)
            self.alert = deepcopy(alert)
            self.equipment = deepcopy(equip)

    def _bump_version(self):
        self.version += 1
        self.last_modified = datetime.utcnow()
        logger.info(f"Global state updated, new version = {self.version}")

    def tick_sim_time(self, delta_seconds:float=1.0):
        if self.sim_paused:
            return
        # 按倍速计算增量
        add_sec = delta_seconds * self.sim_speed
        total = self.sim_time_s + add_sec

        # 进位
        while total >= 60:
            total -= 60
            self.sim_time_m +=1
            if self.sim_time_m >=60:
                self.sim_time_m -=60
                self.sim_time_h +=1
                if self.sim_time_h >=24:
                    self.sim_time_h -=24
                    self.sim_time_day +=1
        self.sim_time_s = total

    def save_snapshot(self):
        if not settings.enable_snapshot:
            return
        snap = self.SnapshotRecord(
            version=self.version,
            ts=self.last_modified,
            env=self.environment,
            crew=self.crew,
            alert=self.alert,
            equip=self.equipment,
        )
        self.snapshots[self.version] = snap
        logger.debug(f"Snapshot saved at version {self.version}")

    def apply_environment_patch(self, patch: EnvironmentStatePatch):
        self.environment = EnvironmentStateAPI.apply_patch(self.environment, patch)
        self._bump_version()
        self.save_snapshot()

    # 新增 crew patch
    def apply_crew_patch(self, patch: CrewStatePatch):
        self.crew = CrewStateAPI.apply_patch(self.crew, patch)
        self._bump_version()
        self.save_snapshot()

    def apply_alert_patch(self, patch: AlertStatePatch):
        self.alert = AlertStateAPI.apply_patch(self.alert, patch)
        self._bump_version()
        self.save_snapshot()

    def apply_equipment_patch(self, patch: EquipmentStatePatch):
        self.equipment = EquipmentStateAPI.apply_patch(self.equipment, patch)
        self._bump_version()
        self.save_snapshot()

    # 列出快照，改成访问对象属性 .version / .ts
    def list_snapshots(self):
        """返回所有快照版本信息，ts转iso字符串给前端"""
        return [
            {"version": snap.version, "ts": snap.ts.isoformat()}
            for snap in self.snapshots.values()
        ]

    def rollback(self, target_version: int):
        """回滚到指定版本，必须deepcopy防止对象引用共享"""
        if target_version not in self.snapshots:
            raise ValueError(f"版本 {target_version} 不存在")
        snap = self.snapshots[target_version]
        self.environment = deepcopy(snap.environment)
        self.crew = deepcopy(snap.crew)
        self.alert = deepcopy(snap.alert)
        self.equipment = deepcopy(snap.equipment)
        self.version = snap.version
        self.last_modified = snap.ts
        logger.info(f"Rollback succeeded to version {target_version}")

global_store = WorldStateStore()