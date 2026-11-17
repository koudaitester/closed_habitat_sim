from fastapi import FastAPI
from src.service import inject_equipment_fault, inject_alert
from src.core.logger import logger

app = FastAPI(title="Fault Injector Service")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fault_injector"}

@app.post("/inject/equipment")
async def api_inject_equipment(device_id: str, fault: bool):
    """手动注入设备故障"""
    ok = await inject_equipment_fault(device_id, fault)
    return {"success": ok}

@app.post("/inject/alert")
async def api_inject_alert(message: str):
    """手动注入告警"""
    ok = await inject_alert(message)
    return {"success": ok}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)
