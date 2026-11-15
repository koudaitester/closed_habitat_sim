#!/bin/bash
mkdir -p fastapi-vision-scaffold/src/{common,core,utils,test}
mkdir -p fastapi-vision-scaffold/src/domains/tune_domain/demos/plant
mkdir -p fastapi-vision-scaffold/src/domains/good_domain/demos/wall

touch fastapi-vision-scaffold/src/common/__init__.py
touch fastapi-vision-scaffold/src/core/__init__.py
touch fastapi-vision-scaffold/src/utils/__init__.py
touch fastapi-vision-scaffold/src/test/__init__.py
touch fastapi-vision-scaffold/src/domains/__init__.py
touch fastapi-vision-scaffold/src/domains/tune_domain/__init__.py
touch fastapi-vision-scaffold/src/domains/tune_domain/demos/__init__.py
touch fastapi-vision-scaffold/src/domains/tune_domain/demos/plant/__init__.py
touch fastapi-vision-scaffold/src/domains/good_domain/__init__.py
touch fastapi-vision-scaffold/src/domains/good_domain/demos/__init__.py
touch fastapi-vision-scaffold/src/domains/good_domain/demos/wall/__init__.py

cat > fastapi-vision-scaffold/.env <<'EOF'
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_VISION_MODEL=moondream
VISION_TIMEOUT=30
EOF

cat > fastapi-vision-scaffold/requirements.txt <<'EOF'
fastapi
uvicorn
pydantic
requests
pydantic-settings
EOF

cat > fastapi-vision-scaffold/main.py <<'EOF'
from fastapi import FastAPI
from domains.tune_domain.api import router as tune_router
from domains.good_domain.api import router as good_router

app = FastAPI()
app.include_router(tune_router)
app.include_router(good_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
EOF

cat > fastapi-vision-scaffold/src/common/vision_client.py <<'EOF'
import requests
from core.config import settings
from core.logger import logger

async def vision_predict(image_b64: str, prompt: str):
    try:
        url = f"{settings.ollama_base_url}/api/chat"
        payload = {
            "model": settings.ollama_vision_model,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64]
                }
            ]
        }
        resp = requests.post(url, json=payload, timeout=settings.vision_timeout)
        resp.raise_for_status()
        res_json = resp.json()
        return res_json["message"]["content"]
    except Exception as e:
        logger.error(f"vision client call error: {str(e)}")
        return "vision_request_failed_no_valid_image"
EOF

cat > fastapi-vision-scaffold/src/core/config.py <<'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ollama_base_url: str
    ollama_vision_model: str
    vision_timeout: int

    class Config:
        env_file = ".env"

settings = Settings()
EOF

cat > fastapi-vision-scaffold/src/core/logger.py <<'EOF'
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("core")
EOF

cat > fastapi-vision-scaffold/src/utils/image_helper.py <<'EOF'
import base64
from pathlib import Path
from typing import Union

SUPPORTED_SUFFIX = {".jpg", ".jpeg", ".png", ".webp"}

def image_to_base64(source: Union[str, Path, bytes]) -> str:
    if isinstance(source, bytes):
        raw = source
    else:
        p = Path(source)
        suffix = p.suffix.lower()
        if suffix not in SUPPORTED_SUFFIX:
            raise ValueError(f"不支持图片格式: {suffix}，支持{SUPPORTED_SUFFIX}")
        raw = p.read_bytes()
    return base64.b64encode(raw).decode("utf-8")

def base64_to_image(b64_str: str, out_path: Union[str, Path]) -> None:
    raw = base64.b64decode(b64_str)
    p = Path(out_path)
    p.write_bytes(raw)
EOF

cat > fastapi-vision-scaffold/src/domains/tune_domain/api.py <<'EOF'
from fastapi import APIRouter
from domains.tune_domain.demos.plant.schema import PlantClassifyReq, PlantClassifyResp
from domains.tune_domain.demos.plant.service import plant_classify
from common.vision_client import vision_predict

router = APIRouter(prefix="/tune")

@router.post("/plant", response_model=PlantClassifyResp)
async def plant_evaluate(req: PlantClassifyReq):
    prompt = "Describe the image objectively. Only tell the visual features of plant, do not judge anything else, do not output json or coordinate data."
    raw_text = await vision_predict(req.image_b64, prompt)
    return await plant_classify(raw_text)
EOF

cat > fastapi-vision-scaffold/src/domains/tune_domain/demos/plant/rules.py <<'EOF'
PLANT_TYPE_MAP = {
    1: "植株健康，叶片翠绿饱满",
    2: "轻微黄叶，少量叶片发黄",
    3: "严重黄叶，较多叶片枯黄",
    4: "枯萎脱水，植株萎蔫",
    5: "霉变腐烂，出现霉斑",
    99: "图片不是植物，无效图片"
}
WARNING_TEXT = "仅外观肉眼观察，无法检测根系内部病害。"
KEY_MAP = {
    1: ["healthy plant", "green leaf", "vibrant"],
    2: ["slight yellow leaf", "few yellow"],
    3: ["many yellow leaf", "heavy yellow"],
    4: ["wilted", "dry", "dehydrated"],
    5: ["mold", "rot", "fungal spot"],
    99: ["not plant", "no plant", "wall", "cloth", "fruit"]
}
EOF

cat > fastapi-vision-scaffold/src/domains/tune_domain/demos/plant/schema.py <<'EOF'
from pydantic import BaseModel, Field
class PlantClassifyReq(BaseModel):
    image_b64: str = Field(..., min_length=1, description="图片base64，非空")
    tag: str | None = None
class PlantClassifyResp(BaseModel):
    type_id: int
    desc: str
    advice: str
    warning: str
EOF

cat > fastapi-vision-scaffold/src/domains/tune_domain/demos/plant/service.py <<'EOF'
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
EOF

cat > fastapi-vision-scaffold/src/domains/good_domain/api.py <<'EOF'
from fastapi import APIRouter
from domains.good_domain.demos.wall.schema import GoodWallClassifyReq, GoodWallClassifyResp
from domains.good_domain.demos.wall.service import goodwall_classify
from common.vision_client import vision_predict

router = APIRouter(prefix="/good")

@router.post("/wall", response_model=GoodWallClassifyResp)
async def wall_evaluate(req: GoodWallClassifyReq):
    prompt = "Describe the image objectively. Only tell the visual features of the wall surface, do not judge anything else, do not output json or coordinate data."
    raw_text = await vision_predict(req.image_b64, prompt)
    return await goodwall_classify(raw_text)
EOF

cat > fastapi-vision-scaffold/src/domains/good_domain/demos/wall/rules.py <<'EOF'
GOODWALL_TYPE_MAP = {
    1: "墙面完好，无破损水渍裂纹",
    2: "细微裂纹，发丝小裂缝",
    3: "起皮脱落，墙皮剥落",
    4: "大片水渍、受潮印记",
    99: "图片不是墙面，无效图片"
}
WARNING_TEXT = "仅外观肉眼参考，无法检测墙体内部渗水与结构性隐患。"
KEY_MAP = {
    1: ["intact wall", "no crack", "clean surface"],
    2: ["fine crack", "small crack", "hairline crack"],
    3: ["peeling paint", "flaking", "wall peel off"],
    4: ["water stain", "wet mark", "moisture stain"],
    99: ["not wall", "no wall", "fruit", "cloth", "plant"]
}
EOF

cat > fastapi-vision-scaffold/src/domains/good_domain/demos/wall/schema.py <<'EOF'
from pydantic import BaseModel, Field
class GoodWallClassifyReq(BaseModel):
    image_b64: str = Field(..., min_length=1, description="图片base64，非空")
    tag: str | None = None
class GoodWallClassifyResp(BaseModel):
    type_id: int
    desc: str
    advice: str
    warning: str
EOF

cat > fastapi-vision-scaffold/src/domains/good_domain/demos/wall/service.py <<'EOF'
from .rules import GOODWALL_TYPE_MAP, KEY_MAP, WARNING_TEXT
async def goodwall_classify(raw_vision_text: str):
    raw_lower = raw_vision_text.lower()
    hit_id = 99
    for tid, keywords in KEY_MAP.items():
        for word in keywords:
            if word in raw_lower:
                hit_id = tid
                break
        if hit_id !=99:
            break
    desc = GOODWALL_TYPE_MAP[hit_id]
    advice_map = {
        1:"墙面状态良好，保持日常通风即可",
        2:"细微裂纹，留意后续是否继续扩大",
        3:"墙皮起皮，建议局部修补墙面",
        4:"存在受潮水渍，优先查找水源，做好防潮",
        99:"未识别到墙面，请重新拍照"
    }
    return {"type_id":hit_id,"desc":desc,"advice":advice_map[hit_id],"warning":WARNING_TEXT}
EOF

cat > fastapi-vision-scaffold/src/test/spec_case_checker.py <<'EOF'
import json

def get_plant_truth():
    from domains.tune_domain.demos.plant.rules import PLANT_TYPE_MAP
    return {"domain":"tune_domain","module":"plant","valid_type_ids":list(PLANT_TYPE_MAP.keys()),"type_desc":PLANT_TYPE_MAP}

def get_wall_truth():
    from domains.good_domain.demos.wall.rules import GOODWALL_TYPE_MAP
    return {"domain":"good_domain","module":"wall","valid_type_ids":list(GOODWALL_TYPE_MAP.keys()),"type_desc":GOODWALL_TYPE_MAP}

def get_all_truth():
    return [get_plant_truth(), get_wall_truth()]

def main():
    with open("src/test/cases.json","r",encoding="utf-8") as f:
        cases = json.load(f)
    truth_list = get_all_truth()
    truth_map = {t["module"]:t for t in truth_list}
    module_case_rec = {}
    for case in cases:
        m = case["module"]
        tid = case["expect_type_id"]
        if m not in module_case_rec:
            module_case_rec[m] = set()
        module_case_rec[m].add(tid)

    print("==================================================")
    print("          真值业务分支校验报告")
    print("==================================================")
    for mod_name, truth in truth_map.items():
        valid_ids = set(truth["valid_type_ids"])
        covered = module_case_rec.get(mod_name, set())
        missing = valid_ids - covered
        print(f"【模块：{mod_name}】")
        print(f"基准合法type_id: {sorted(list(valid_ids))}")
        print(f"已覆盖type_id: {sorted(list(covered))}")
        if missing:
            print(f"❌缺失分支type_id: {sorted(list(missing))}")
        else:
            print(f"❌缺失分支type_id: []")
        print()

if __name__ == "__main__":
    main()
EOF

cat > fastapi-vision-scaffold/src/test/cases.json <<'EOF'
[
{"module":"plant","case_name":"健康植株","expect_type_id":1},
{"module":"plant","case_name":"轻微黄叶","expect_type_id":2},
{"module":"plant","case_name":"严重黄叶","expect_type_id":3},
{"module":"plant","case_name":"枯萎脱水","expect_type_id":4},
{"module":"plant","case_name":"霉变腐烂","expect_type_id":5},
{"module":"plant","case_name":"非植物图片","expect_type_id":99},
{"module":"wall","case_name":"完好墙面","expect_type_id":1},
{"module":"wall","case_name":"细微发丝裂纹","expect_type_id":2},
{"module":"wall","case_name":"墙皮起皮脱落","expect_type_id":3},
{"module":"wall","case_name":"大片受潮水渍","expect_type_id":4},
{"module":"wall","case_name":"非墙面图片","expect_type_id":99}
]
EOF

chmod +x fastapi-vision-scaffold/create_scaffold.sh
echo "脚手架创建完成，进入目录执行：python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"

