"""
配置管理测试
"""

import pytest
from src.core.config import Config


@pytest.mark.asyncio
async def test_config_loading():
    """测试配置加载"""
    config = Config.load()

    # 检查基本配置
    assert config.agent.name == "MyAgent"
    assert config.agent.version == "0.1.0"

    # 检查 LLM 配置
    assert config.settings.llm_provider in ["claude", "openai", "deepseek", "kimi", "minimax"]

    # 检查记忆配置
    assert config.memory.short_term.max_turns > 0


@pytest.mark.asyncio
async def test_llm_config():
    """测试 LLM 配置获取"""
    config = Config.load()

    # 获取 Claude 配置
    claude_config = config.get_llm_config("claude")
    assert claude_config["provider"] == "claude"
    assert claude_config["model"] is not None

    # 获取 OpenAI 配置
    openai_config = config.get_llm_config("openai")
    assert openai_config["provider"] == "openai"
    assert openai_config["model"] is not None
