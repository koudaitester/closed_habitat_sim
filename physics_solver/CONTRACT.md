# Closed Habitat Simulation - CONTRACT.md
## 一、系统总契约
本契约定义微服务之间接口、事件、数据模型约定，所有服务必须遵守。
> 服务清单：world-state（状态仓库+事件总线）、physics_solver（物理仿真）、fault_injector（故障注入，待实现）

## 二、HTTP接口约定（world-state）
1. GET /api/worldstate
用途：读取全局最新状态（唯一真值源 global_store）
返回：完整json，包含四大domain：environment / crew / equipment / alert，附带全局version。

2. POST /api/event/submit
用途：外部服务推送patch事件（physics_solver、fault_injector使用）
请求体结构：
{
  "type": "xxx.state.patch",
  "payload": {}
}

> 遗留备注：系统还存在旧接口 /event，顶层字段名与/api/event/submit不一致，两套事件入口，后续统一。

3. GET /state/latest
用途：前端旧快照接口
⚠️ 问题：快照不会自动跟随global_store更新，目前为静态快照，前端暂不推荐使用。

## 三、事件定义规范
事件统一命名模板：`{domain}.state.patch`
含义：增量局部更新，仅传入需要修改的字段，其余状态保留。

已定义事件列表：
1. environment.state.patch
payload：{"temperature":float, "co2_ppm":float}
作用：更新舱内环境参数

2. crew.state.patch
payload：乘员相关增量字段
作用：更新乘员状态

3. equipment.state.patch
payload：设备增量状态
作用：更新设备运行状态

4. alert.state.patch
payload：告警信息
作用：新增/修改告警

## 四、已知BUG与技术债务
1. physics_solver 读取crew域，代码写crew_members，实际schema字段名称是members，导致crew_count恒等于0。
2. physics_solver读取equipment使用扁平字段o2_generator.active；真实数据结构是devices[]设备列表，读取逻辑不匹配。
3. event_bus.py：顶部handlers字典定义，但代码未使用，当前事件路由靠if-elif硬编码分支。
4. 前端dashboard：当前读取/state/latest快照，不和global_store同步；只绑定第一个卡片，crew/equipment/alert卡片没有绑定数据。
5. update_environment_state 函数被导入，但没有被调用（遗留死代码）。

## 五、数据流
physics_solver：GET拉取/api/worldstate → 物理仿真计算 → POST推送xxx.state.patch → world-state event_bus路由 → 更新global_store → 前端读取/api/worldstate展示
