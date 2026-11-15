from .rules import PLANT_TYPE_MAP, KEY_MAP, WARNING_TEXT
async def plant_classify(raw_vision_text: str):
    raw_lower = raw_vision_text.lower()
    hit_id = 99
    for tid, keywords in KEY_MAP.items():
        for word in keywords:
            if word in raw_lower:
                hit_id = tid
                break
        if hit_id !=99:
            break
    desc = PLANT_TYPE_MAP[hit_id]
    advice_map = {
        1:"植物状态健康，维持现有养护节奏",
        2:"少量黄叶，检查光照与浇水频次",
        3:"黄叶较多，减少浇水，排查是否烂根",
        4:"植株萎蔫脱水，及时补水",
        5:"存在霉斑腐烂，隔离清理病叶",
        99:"未识别到植物，请重新拍照"
    }
    return {"type_id":hit_id,"desc":desc,"advice":advice_map[hit_id],"warning":WARNING_TEXT}
