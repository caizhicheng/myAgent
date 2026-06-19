"""
交互通道模块
"""

from src.channels.base import Channel
from src.channels.cli import CLIChannel

__all__ = ["Channel", "CLIChannel"]
