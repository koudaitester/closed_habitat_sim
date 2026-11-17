# main.py
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

from src.core.config import settings
from src.core.logger import logger
from src.client.worldstate_client import worldstate_client
from src.solver.service import build_mock_world_state, run_physical_tick

app = FastAPI(title="Physics Solver")

# 后台tick循环开关
is_running = True

class TickResponse(BaseModel):
    success: bool
    new_environment: dict | None = None

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "physics_solver"}

@app.post("/api/tick", response_model=TickResponse)
async def manual_tick():
    """手动执行单次物理求解，用于调试"""
    ws_data = await worldstate_client.get_world_state()
    if not ws_data:
        return {"success": False}
    result = run_physical_tick(ws_data, delta_sec=settings.TICK_INTERVAL_SEC)
    # 组装事件，推回world-state
    event_payload = {
        "type": "environment.update",
        "payload": result
    }

    await worldstate_client.submit_event(event_payload)
    return {"success": True, "new_environment": result}


@app.on_event("startup")
async def startup_task():
    """启动后台自动tick循环"""
    async def auto_tick_loop():
        global is_running
        while is_running:
            try:
                ws_data = await worldstate_client.get_world_state()
                if ws_data:
                    result = run_physical_tick(ws_data, delta_sec=settings.TICK_INTERVAL_SEC)
                    event_payload = {
                        "type": "environment.update",
                        "payload": result
                    }
                    await worldstate_client.submit_event(event_payload)
            except Exception as e:
                logger.exception("自动tick计算异常")
            await asyncio.sleep(settings.TICK_INTERVAL_SEC)
    asyncio.create_task(auto_tick_loop())

@app.post("/api/tick_mock", response_model=TickResponse)
async def mock_tick():
    """本地桩数据测试，不调用world-state，单独测试物理求解"""
    mock_ws = build_mock_world_state()
    result = run_physical_tick(mock_ws, delta_sec=settings.TICK_INTERVAL_SEC)
    return {"success": True, "new_environment": result}


@app.on_event("shutdown")
async def shutdown_task():
    global is_running
    is_running = False
    logger.info("Physics Solver 服务关闭，停止tick循环")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
