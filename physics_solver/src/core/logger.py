# src/core/logger.py
import logging
from src.core.config import settings

logger = logging.getLogger("physics_solver")
logger.setLevel(settings.LOG_LEVEL)

console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
