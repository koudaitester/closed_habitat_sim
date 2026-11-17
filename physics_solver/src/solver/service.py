# src/solver/service.py
from src.core.logger import logger
from src.solver.rules import calc_gas_and_thermal

def build_mock_world_state():
    return {
        "environment": {
            "temperature": 22.0,
            "humidity": 50.0,
            "co2_ppm": 400.0,
            "vapor_pressure": 2.3
        },
        "crew": {
            "crew_members": [
                {"id":1, "name":"crew_01"}
            ]
        },
        "equipment": {
            "o2_generator": {"active": True},
            "co2_scrubber": {"active": False}, # CO2洗涤器停机
            "cooling_loop": {"active": True},
            "hull": {"leak": False}
        }
    }



def run_physical_tick(ws_data: dict, delta_sec: float = 1.0):
    """单次物理步进"""
    env = ws_data["environment"]
    equipment = ws_data["equipment"]
    crew = ws_data["crew"]

    # 提取参数
    temp = env.get("temperature", 22.0) or 22.0
    co2_ppm = env.get("co2_ppm", 400.0) or 400.0
    
    # 安全获取乘员列表，key不存在返回空数组，避免KeyError
    crew_members = crew.get("crew_members", [])
    crew_count = len(crew_members)
    logger.info(f"crew_count: {crew_count}")

    # 设备状态提取
    o2_generator_on = equipment.get("o2_generator", {}).get("active", False)
    co2_scrubber_on = equipment.get("co2_scrubber", {}).get("active", False)
    cooling_active = equipment.get("cooling_loop", {}).get("active", False)
    hull_leak = equipment.get("hull", {}).get("leak", False)

    result = calc_gas_and_thermal(
        temp=temp,
        co2_ppm=co2_ppm,
        crew_num=crew_count,
        has_o2_generator=o2_generator_on,
        has_co2_scrubber=co2_scrubber_on,
        has_cooling=cooling_active,
        has_leak=hull_leak,
        delta_sec=delta_sec
    )
    return result
