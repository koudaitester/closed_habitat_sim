# 密闭栖息地仿真 · 接口与事件契约

> 用途：改代码/联调前先扫一眼这份，别靠记忆。只记契约，不记实现。

---

## 1. 服务清单

| 服务 | 端口 | 职责 |
|---|---|---|
| world-state | 8000 | 全局状态仓库 + 事件总线，**不做计算** |
| physics_solver | 8001 | 物理推演，算完推 patch 事件 |
| fault_injector | — | 待开发，人为注入故障 |
| dashboard（前端） | 跟 8000 同源 | 只读展示，不参与计算 |

启动：
```bash
# world_state
cd world_state && python main.py
# physics_solver
cd physics_solver && python main.py
```

---

## 2. HTTP 接口

### world-state (8000)

| 方法 | 路径 | 入参 | 说明 |
|---|---|---|---|
| GET | `/` | — | 前端看板 dashboard.html |
| GET | `/health` | — | 健康检查 |
| GET | `/api/worldstate` | — | 返回整个 global_store 对象（physics 用这个） |
| GET | `/state/latest` | — | `{version,last_modified,environment,crew,alert,equipment}`（**前端用这个**） |
| POST | `/event` | `{event_type,payload,source}` | 事件入口 A（**前端用这个**） |
| POST | `/api/event/submit` | `{type,payload}` | 事件入口 B（source 硬编码 `physics_solver`） |
| GET | `/snapshots/list` | — | `[{version,ts}]` |
| POST | `/snapshots/rollback?version=N` | query | 回滚到快照版本 |
| GET/PATCH/PUT/DELETE | `/domain/{域}/state` | — | 各域 CRUD，四个域都有 |

> ⚠️ 两个事件入口并存（`/event` 和 `/api/event/submit`），信封字段名不同：`event_type` vs `type`。**同一个事件必须走对入口，否则必报错。**

### physics_solver (8001)

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查 |
| POST | `/api/tick` | 手动单步：读 state → 算 → 推事件 |
| POST | `/api/tick_mock` | 桩数据单测，不连 world-state |

---

## 3. 事件契约

### 信封格式
```json
{
  "event_type": "environment.update",
  "payload": {},
  "source": "physics_solver"
}
```

### 已注册事件类型

| event_type | payload 结构 | 落到哪 |
|---|---|---|
| `environment.update` | `{"temperature":float,"co2_ppm":float}` | `apply_environment_patch` |
| `crew.state.patch` | `CrewStatePatch` | `apply_crew_patch` |
| `alert.state.patch` | `AlertStatePatch` | `apply_alert_patch` |
| `equipment.state.patch` | `EquipmentStatePatch` | `apply_equipment_patch` |

> ⚠️ 命名不统一：环境域用 `environment.update`，其他三域用 `xxx.state.patch`。新增域建议统一成 `xxx.state.patch`。

---

## 4. 四个域字段（唯一事实来源）

### environment_state
```
temperature      温度 ℃        Optional[float]
humidity         相对湿度 %     Optional[float]
co2_ppm          二氧化碳 ppm   Optional[float]
vapor_pressure   水汽分压 kPa    Optional[float]
```

### crew_state
```
members: [ {member_id:str, name:str, health:0~100, fatigue:0~100, emotion:0~100, task_id:str|null} ]
total_count: int
```

### alert_state
```
alerts: [ {alert_id:str, title:str, level:"info"|"warning"|"critical", source:str, is_resolved:bool} ]
```

### equipment_state
```
devices: [ {equip_id:str, name:str, category:str, status:"normal"|"warning"|"fault"|"offline", power:0~100} ]
```

### store 附加字段
```
version        int    每次 apply_patch +1
last_modified  datetime
sim_time_day / sim_time_h / sim_time_m / sim_time_s
sim_paused     bool   默认 True（暂停）
sim_speed      float  默认 1.0
snapshots      Dict[version -> SnapshotRecord]
```

---

## 5. ⚠️ 当前已知的字段错位（联调前必查）

| # | 位置 | 问题 |
|---|---|---|
| 1 | `physics_solver/src/solver/service.py:39` | 读 `crew.get("crew_members")`，**实际字段是 `crew.members`** → `crew_count` 恒为 0 → CO₂ 永远不涨 |
| 2 | `physics_solver/src/solver/service.py:44-47` | 读 `equipment.o2_generator.active` 等扁平结构，**实际是 `equipment.devices[]` 列表** → 设备状态恒为 False |
| 3 | `physics_solver/src/solver/schema.py` | `EnvPhysicalResult` 定义了 `oxygen/pressure/event_type`，但 `rules.py` 实际返回 dict 只有 `temperature/co2_ppm` → 这个类是死代码 |
| 4 | `event_bus.py` 顶部 `handlers` 字典 | 定义了但 `handle_event` 全靠 if/elif 硬编码，**这个字典没被使用** → 死代码，别被它误导 |
| 5 | `event_bus.py:5` | 顶部 `import update_environment_state`，但那个函数直接改属性、不走 `apply_patch`，**没有被调用** |

---

## 6. 数据流

```
world-state (状态仓库)
   ↑ GET /api/worldstate
physics_solver (计算)
   ↓ POST /api/event/submit   {"type":"environment.update","payload":{temperature,co2_ppm}}
event_bus.handle_event → apply_environment_patch → global_store 更新, version+1
   ↓
dashboard 轮询 /state/latest 展示
```
