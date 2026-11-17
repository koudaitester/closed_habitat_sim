# main.py
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, responses, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 将src加入模块搜索路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.domains.environment_state import router as environment_router
from src.domains.crew_state import router as crew_router
from src.event_bus import event_bus, EventEnvelope
from src.core.logger import logger
from src.store import global_store
from src.domains.alert_state import router as alert_router
from src.domains.equipment_state.facade import router as equipment_router
import sys
import os
from pydantic import BaseModel
from src.event_bus import event_bus 

app = FastAPI(title="World-State 密闭栖息地状态服务", version="0.1.0")

# 挂载环境域独立调试接口
app.include_router(environment_router)
app.include_router(crew_router)
app.include_router(alert_router)
app.include_router(equipment_router)

class EventIn(BaseModel):
    type: str
    payload: dict

def get_resource_path(relative_path: str):
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller打包后的临时解压目录
        base_path = sys._MEIPASS
    else:
        # 开发状态
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# world-state main.py 添加这个接口
@app.get("/api/worldstate")
async def get_worldstate():
    return global_store

# ========== 全局事件总线入口（外部仿真服务使用） ==========
@app.post("/event")
def receive_external_event(envelope: EventEnvelope):
    """全局事件接收入口，外部Agent/physics服务统一推送状态变更事件"""
    try:
        result = event_bus.handle_event(envelope)
        return {
            "status": "success",
            "data": result,
            "global_version": global_store.version
        }
    except ValueError as e:
        logger.error(f"Event handle error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ========== 全局状态读取接口 ==========
@app.get("/state/latest")
def get_full_global_state():
    """读取全部域当前全局状态"""
    return {
        "version": global_store.version,
        "last_modified": global_store.last_modified,
        "environment": global_store.environment,
        "crew": global_store.crew,
        "alert": global_store.alert,
        "equipment": global_store.equipment,
    }

# world-state main.py
from src.event_bus import EventEnvelope

@app.post("/api/event/submit")
async def event_submit(event_in: dict):
# 把http传进来的dict，包装成总线需要的Envelope实例
    envelope = EventEnvelope(
        event_type=event_in["type"],
        payload=event_in["payload"],
        source=event_in.get("source", "unknown") # 从请求体读取source，没有就填unknown
    )
    event_bus.handle_event(envelope)  # 补上 await！
    logger.info(f"Event {event_in['type']} submitted, source={envelope.source}")
    return {"ok": True, "event_type": event_in["type"]}


# 获取快照列表
@app.get("/snapshots/list")
def get_snapshot_list():
    try:
        return global_store.list_snapshots()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 执行回滚
@app.post("/snapshots/rollback")
def rollback(version: int = Query(...)):
    try:
        global_store.rollback(version)
        return {"ok": True, "msg": f"成功回滚到版本 {version}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
# ✅ 正确
static_dir = get_resource_path("src/web/static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def index():
    html_path = get_resource_path("src/web/templates/dashboard.html")
    return FileResponse(html_path)

# ========== 健康检查 ==========
@app.get("/health")
def health_check():
    return {"service": "world-state", "status": "ok"}


if __name__ == "__main__":
    import uvicorn
    from src.core.config import settings
    uvicorn.run(app, host=settings.host, port=settings.port, reload=False)
