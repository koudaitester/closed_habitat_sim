# src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 服务基础配置
    service_name: str = "world-state"
    host: str = "127.0.0.1"
    port: int = 8000

    # 快照配置
    enable_snapshot: bool = True
    snapshot_memory_only: bool = True  # 先内存存储，后续再接入文件持久化

    # 仿真基础参数
    sim_time_step: float = 1.0

settings = Settings()
