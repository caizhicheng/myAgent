"""
记忆管理器
整合短期记忆和长期记忆
"""

from typing import Dict, List, Optional

from loguru import logger

from src.core.config import config
from src.memory.long_term import LongTermMemory
from src.memory.short_term import ShortTermMemory


class MemoryManager:
    """记忆管理器"""

    def __init__(self):
        """初始化记忆管理器"""
        self.short_term = ShortTermMemory(
            db_path=config.memory.short_term.database,
            max_turns=config.memory.short_term.max_turns,
        )
        self.long_term = LongTermMemory(db_path=config.memory.long_term.database)
        self._initialized = False

    async def initialize(self):
        """初始化记忆系统"""
        if self._initialized:
            return

        await self.short_term.initialize()
        await self.long_term.initialize()
        self._initialized = True
        logger.info("记忆管理器初始化完成")

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ):
        """
        添加消息到短期记忆

        Args:
            session_id: 会话 ID
            role: 角色
            content: 内容
            metadata: 元数据
        """
        if not self._initialized:
            await self.initialize()

        await self.short_term.add_message(session_id, role, content, metadata)

    async def get_conversation_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[Dict]:
        """
        获取对话历史

        Args:
            session_id: 会话 ID
            limit: 限制数量

        Returns:
            消息列表
        """
        if not self._initialized:
            await self.initialize()

        return await self.short_term.get_messages(session_id, limit)

    async def clear_conversation(self, session_id: str):
        """
        清空对话历史

        Args:
            session_id: 会话 ID
        """
        if not self._initialized:
            await self.initialize()

        await self.short_term.clear_session(session_id)

    async def store_knowledge(
        self,
        key: str,
        value,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ):
        """
        存储知识到长期记忆

        Args:
            key: 键
            value: 值
            category: 分类
            tags: 标签
            metadata: 元数据
        """
        if not self._initialized:
            await self.initialize()

        await self.long_term.store(key, value, category, tags, metadata)

    async def retrieve_knowledge(self, key: str) -> Optional[Dict]:
        """
        从长期记忆检索知识

        Args:
            key: 键

        Returns:
            知识字典
        """
        if not self._initialized:
            await self.initialize()

        return await self.long_term.retrieve(key)

    async def search_knowledge(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        搜索知识

        Args:
            query: 搜索关键词
            category: 分类
            tags: 标签
            limit: 限制数量

        Returns:
            知识列表
        """
        if not self._initialized:
            await self.initialize()

        return await self.long_term.search(query, category, tags, limit)

    async def save_conversation_summary(
        self, session_id: str, summary: str, key_points: Optional[List[str]] = None
    ):
        """
        保存对话摘要

        Args:
            session_id: 会话 ID
            summary: 摘要
            key_points: 关键点
        """
        if not self._initialized:
            await self.initialize()

        await self.long_term.store_conversation_summary(session_id, summary, key_points)

    async def get_conversation_summary(self, session_id: str) -> Optional[Dict]:
        """
        获取对话摘要

        Args:
            session_id: 会话 ID

        Returns:
            摘要字典
        """
        if not self._initialized:
            await self.initialize()

        return await self.long_term.get_conversation_summary(session_id)

    async def search_messages(self, session_id: str, keyword: str) -> List[Dict]:
        """
        搜索消息

        Args:
            session_id: 会话 ID
            keyword: 关键词

        Returns:
            匹配的消息列表
        """
        if not self._initialized:
            await self.initialize()

        return await self.short_term.search_messages(session_id, keyword)

    async def close(self):
        """关闭记忆系统"""
        await self.short_term.close()
        await self.long_term.close()
        self._initialized = False
        logger.info("记忆管理器已关闭")
