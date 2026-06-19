"""
日志工具
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(log_file: str = "logs/agent.log", level: str = "INFO"):
    """
    设置日志

    Args:
        log_file: 日志文件路径
        level: 日志级别
    """
    # 移除默认处理器
    logger.remove()

    # 添加控制台输出
    logger.add(
        sink=sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )

    # 添加文件输出
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        sink=str(log_path),
        rotation="10 MB",
        retention="7 days",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
    )

    logger.info(f"日志系统初始化完成，日志级别: {level}")
