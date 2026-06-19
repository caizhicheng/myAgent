"""
记忆系统测试
"""

import pytest
from src.memory.short_term import ShortTermMemory
from src.memory.long_term import LongTermMemory
from src.memory.manager import MemoryManager


@pytest.mark.asyncio
async def test_short_term_memory():
    """测试短期记忆"""
    memory = ShortTermMemory(db_path="./data/test/memory_test.db")

    try:
        # 初始化
        await memory.initialize()

        # 添加消息
        await memory.add_message("test_session", "user", "你好")
        await memory.add_message("test_session", "assistant", "你好！有什么可以帮助你的吗？")

        # 获取消息
        messages = await memory.get_messages("test_session")

        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "你好"
        assert messages[1]["role"] == "assistant"

        # 清空会话
        await memory.clear_session("test_session")
        messages = await memory.get_messages("test_session")
        assert len(messages) == 0

    finally:
        await memory.close()


@pytest.mark.asyncio
async def test_long_term_memory():
    """测试长期记忆"""
    memory = LongTermMemory(db_path="./data/test/knowledge_test.db")

    try:
        # 初始化
        await memory.initialize()

        # 存储知识
        await memory.store(
            key="test_key",
            value="test_value",
            category="test",
            tags=["tag1", "tag2"],
        )

        # 检索知识
        result = await memory.retrieve("test_key")
        assert result is not None
        assert result["key"] == "test_key"
        assert result["value"] == "test_value"
        assert result["category"] == "test"

        # 搜索知识
        results = await memory.search(query="test", category="test")
        assert len(results) > 0

        # 删除知识
        await memory.delete("test_key")
        result = await memory.retrieve("test_key")
        assert result is None

    finally:
        await memory.close()


@pytest.mark.asyncio
async def test_memory_manager():
    """测试记忆管理器"""
    manager = MemoryManager()

    try:
        # 初始化
        await manager.initialize()

        # 测试短期记忆
        await manager.add_message("test_session", "user", "测试消息")
        history = await manager.get_conversation_history("test_session")
        assert len(history) > 0

        # 测试长期记忆
        await manager.store_knowledge("test_knowledge", "测试知识", category="test")
        knowledge = await manager.retrieve_knowledge("test_knowledge")
        assert knowledge is not None

    finally:
        await manager.close()
