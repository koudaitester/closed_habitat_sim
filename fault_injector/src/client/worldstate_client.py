import httpx
from src.core.config import settings
from src.core.logger import logger

class WorldStateClient:
    def __init__(self):
        self.base_url = settings.WORLD_STATE_URL

    async def submit_event(self, event_payload: dict):
        url = f"{self.base_url}/api/event/submit"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=event_payload, timeout=5.0)
                resp.raise_for_status()
                # 改回读取 type，加get防止报错
                logger.info(f"事件推送成功 type={event_payload.get('type')}")
                return True
        except Exception as e:
            logger.error(f"推送事件失败: {e}")
            return False