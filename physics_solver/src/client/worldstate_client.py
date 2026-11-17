import httpx
from src.core.config import settings
from src.core.logger import logger

class WorldStateClient:
    def __init__(self):
        self.base_url = settings.WORLD_STATE_URL

    async def get_world_state(self):
        """获取完整全局world state"""
        url = f"{self.base_url}/api/worldstate"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=5.0)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"获取world state失败: {e}")
            return None

    async def submit_event(self, event_payload: dict):
        """提交事件到world-state事件总线"""
        url = f"{self.base_url}/api/event/submit"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url,
                    json=event_payload,
                    timeout=5.0
                )
                resp.raise_for_status()
                logger.info(f"事件推送成功 type={event_payload.get('type')}")
                return resp.json()
        except Exception as e:
            logger.error(f"推送事件失败: {e}, payload={event_payload}")
            return None

# 全局单例
worldstate_client = WorldStateClient()
