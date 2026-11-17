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
