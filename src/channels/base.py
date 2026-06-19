"""
通道基类
定义交互通道的基本接口
"""

from abc import ABC, abstractmethod


class Channel(ABC):
    """通道基类"""

    @abstractmethod
    async def start(self):
        """启动通道"""
        pass

    @abstractmethod
    async def stop(self):
        """停止通道"""
        pass

    @abstractmethod
    async def send_message(self, message: str):
        """
        发送消息

        Args:
            message: 消息内容
        """
        pass
