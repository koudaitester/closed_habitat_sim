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
