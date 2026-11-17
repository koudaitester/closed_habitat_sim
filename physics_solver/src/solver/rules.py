"""
物理求解规则：密闭舱内气体、热学简易模型
单位：
co2_ppm : 二氧化碳浓度 ppm
temperature : ℃
"""

def calc_gas_and_thermal(
    temp: float,
    co2_ppm: float,
    crew_num: int,
    has_o2_generator: bool,
    has_co2_scrubber: bool,
    has_cooling: bool,
    has_leak: bool,
    delta_sec: float = 1.0
):
    # 基础消耗/生成速率
    crew_co2_produce_per_sec_ppm = 0.04   # 单人每秒增加CO2(ppm)
    co2_scrubber_rate_ppm = -0.035        # CO2洗涤器，负值代表减少

    # 温度
    heat_total = crew_num * 0.008 + 0.015
    if has_cooling:
        heat_total += -0.035
    new_temp = temp + heat_total * delta_sec
    new_temp = max(5, min(60, new_temp))

    # CO2计算
    co2_delta = crew_num * crew_co2_produce_per_sec_ppm * delta_sec
    if has_co2_scrubber:
        co2_delta += co2_scrubber_rate_ppm * delta_sec
    new_co2_ppm = co2_ppm + co2_delta
    new_co2_ppm = max(0, min(50000, new_co2_ppm))

    return {
        "temperature": round(new_temp,3),
        "co2_ppm": round(new_co2_ppm,3)
    }
