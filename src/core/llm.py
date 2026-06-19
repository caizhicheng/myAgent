"""
LLM 适配层
提供统一的 LLM 接口，支持多种模型
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from loguru import logger


class Message:
    """消息类"""

    def __init__(self, role: str, content: str):
        """
        初始化消息

        Args:
            role: 角色 (system, user, assistant)
            content: 消息内容
        """
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {"role": self.role, "content": self.content}

    def __repr__(self) -> str:
        return f"Message(role={self.role}, content={self.content[:50]}...)"


class LLMProvider(ABC):
    """LLM 提供者基类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 LLM 提供者

        Args:
            config: 配置字典
        """
        self.config = config
        self.model = config.get("model")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)

    @abstractmethod
    async def chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> str:
        """
        同步对话

        Args:
            messages: 消息列表
            tools: 工具列表
            **kwargs: 其他参数

        Returns:
            响应文本
        """
        pass

    @abstractmethod
    async def stream_chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> AsyncIterator[str]:
        """
        流式对话

        Args:
            messages: 消息列表
            tools: 工具列表
            **kwargs: 其他参数

        Yields:
            响应文本片段
        """
        pass

    @abstractmethod
    async def chat_with_tools(
        self, messages: List[Message], tools: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """
        带工具调用的对话

        Args:
            messages: 消息列表
            tools: 工具列表
            **kwargs: 其他参数

        Returns:
            包含响应和工具调用的字典
        """
        pass


class ClaudeProvider(LLMProvider):
    """Claude 提供者"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from langchain_anthropic import ChatAnthropic

            self.client = ChatAnthropic(
                api_key=config.get("api_key"),
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            logger.info(f"Claude 提供者初始化成功: {self.model}")
        except Exception as e:
            logger.error(f"Claude 提供者初始化失败: {e}")
            raise

    async def chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> str:
        """同步对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            # 转换消息格式
            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            # 调用模型
            response = await self.client.ainvoke(lc_messages)
            return response.content

        except Exception as e:
            logger.error(f"Claude 对话失败: {e}")
            raise

    async def stream_chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> AsyncIterator[str]:
        """流式对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            # 转换消息格式
            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            # 流式调用
            async for chunk in self.client.astream(lc_messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Claude 流式对话失败: {e}")
            raise

    async def chat_with_tools(
        self, messages: List[Message], tools: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """带工具调用的对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            from langchain_core.tools import tool

            # 转换消息格式
            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            # 绑定工具
            llm_with_tools = self.client.bind_tools(tools)

            # 调用模型
            response = await llm_with_tools.ainvoke(lc_messages)

            result = {"content": response.content, "tool_calls": []}

            # 提取工具调用
            if hasattr(response, "tool_calls") and response.tool_calls:
                result["tool_calls"] = response.tool_calls

            return result

        except Exception as e:
            logger.error(f"Claude 工具调用失败: {e}")
            raise


class OpenAIProvider(LLMProvider):
    """OpenAI 提供者"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from langchain_openai import ChatOpenAI

            self.client = ChatOpenAI(
                api_key=config.get("api_key"),
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            logger.info(f"OpenAI 提供者初始化成功: {self.model}")
        except Exception as e:
            logger.error(f"OpenAI 提供者初始化失败: {e}")
            raise

    async def chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> str:
        """同步对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            response = await self.client.ainvoke(lc_messages)
            return response.content

        except Exception as e:
            logger.error(f"OpenAI 对话失败: {e}")
            raise

    async def stream_chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> AsyncIterator[str]:
        """流式对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            async for chunk in self.client.astream(lc_messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"OpenAI 流式对话失败: {e}")
            raise

    async def chat_with_tools(
        self, messages: List[Message], tools: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """带工具调用的对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            llm_with_tools = self.client.bind_tools(tools)
            response = await llm_with_tools.ainvoke(lc_messages)

            result = {"content": response.content, "tool_calls": []}

            if hasattr(response, "tool_calls") and response.tool_calls:
                result["tool_calls"] = response.tool_calls

            return result

        except Exception as e:
            logger.error(f"OpenAI 工具调用失败: {e}")
            raise


class DeepSeekProvider(LLMProvider):
    """DeepSeek 提供者"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from langchain_openai import ChatOpenAI

            self.client = ChatOpenAI(
                api_key=config.get("api_key"),
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                base_url=config.get("base_url", "https://api.deepseek.com/v1"),
            )
            logger.info(f"DeepSeek 提供者初始化成功: {self.model}")
        except Exception as e:
            logger.error(f"DeepSeek 提供者初始化失败: {e}")
            raise

    async def chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> str:
        """同步对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            response = await self.client.ainvoke(lc_messages)
            return response.content

        except Exception as e:
            logger.error(f"DeepSeek 对话失败: {e}")
            raise

    async def stream_chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> AsyncIterator[str]:
        """流式对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            async for chunk in self.client.astream(lc_messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"DeepSeek 流式对话失败: {e}")
            raise

    async def chat_with_tools(
        self, messages: List[Message], tools: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """带工具调用的对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            llm_with_tools = self.client.bind_tools(tools)
            response = await llm_with_tools.ainvoke(lc_messages)

            result = {"content": response.content, "tool_calls": []}

            if hasattr(response, "tool_calls") and response.tool_calls:
                result["tool_calls"] = response.tool_calls

            return result

        except Exception as e:
            logger.error(f"DeepSeek 工具调用失败: {e}")
            raise


class KimiProvider(LLMProvider):
    """Kimi (Moonshot) 提供者"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from langchain_openai import ChatOpenAI

            self.client = ChatOpenAI(
                api_key=config.get("api_key"),
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                base_url=config.get("base_url", "https://api.moonshot.cn/v1"),
            )
            logger.info(f"Kimi 提供者初始化成功: {self.model}")
        except Exception as e:
            logger.error(f"Kimi 提供者初始化失败: {e}")
            raise

    async def chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> str:
        """同步对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            response = await self.client.ainvoke(lc_messages)
            return response.content

        except Exception as e:
            logger.error(f"Kimi 对话失败: {e}")
            raise

    async def stream_chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> AsyncIterator[str]:
        """流式对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            async for chunk in self.client.astream(lc_messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Kimi 流式对话失败: {e}")
            raise

    async def chat_with_tools(
        self, messages: List[Message], tools: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """带工具调用的对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            llm_with_tools = self.client.bind_tools(tools)
            response = await llm_with_tools.ainvoke(lc_messages)

            result = {"content": response.content, "tool_calls": []}

            if hasattr(response, "tool_calls") and response.tool_calls:
                result["tool_calls"] = response.tool_calls

            return result

        except Exception as e:
            logger.error(f"Kimi 工具调用失败: {e}")
            raise


class MinimaxProvider(LLMProvider):
    """Minimax 提供者"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from langchain_openai import ChatOpenAI

            # Minimax 使用 OpenAI 兼容接口
            base_url = "https://api.minimax.chat/v1"
            self.client = ChatOpenAI(
                api_key=config.get("api_key"),
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                base_url=base_url,
            )
            self.group_id = config.get("group_id")
            logger.info(f"Minimax 提供者初始化成功: {self.model}")
        except Exception as e:
            logger.error(f"Minimax 提供者初始化失败: {e}")
            raise

    async def chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> str:
        """同步对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            response = await self.client.ainvoke(lc_messages)
            return response.content

        except Exception as e:
            logger.error(f"Minimax 对话失败: {e}")
            raise

    async def stream_chat(
        self, messages: List[Message], tools: Optional[List[Dict]] = None, **kwargs
    ) -> AsyncIterator[str]:
        """流式对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            async for chunk in self.client.astream(lc_messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Minimax 流式对话失败: {e}")
            raise

    async def chat_with_tools(
        self, messages: List[Message], tools: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """带工具调用的对话"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            for msg in messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            llm_with_tools = self.client.bind_tools(tools)
            response = await llm_with_tools.ainvoke(lc_messages)

            result = {"content": response.content, "tool_calls": []}

            if hasattr(response, "tool_calls") and response.tool_calls:
                result["tool_calls"] = response.tool_calls

            return result

        except Exception as e:
            logger.error(f"Minimax 工具调用失败: {e}")
            raise


class LLMFactory:
    """LLM 工厂类"""

    _providers = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        "deepseek": DeepSeekProvider,
        "kimi": KimiProvider,
        "minimax": MinimaxProvider,
    }

    @classmethod
    def create(cls, provider: str, config: Dict[str, Any]) -> LLMProvider:
        """
        创建 LLM 提供者

        Args:
            provider: 提供者名称
            config: 配置字典

        Returns:
            LLM 提供者实例
        """
        if provider not in cls._providers:
            raise ValueError(f"不支持的 LLM 提供者: {provider}")

        provider_class = cls._providers[provider]
        return provider_class(config)

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        注册自定义提供者

        Args:
            name: 提供者名称
            provider_class: 提供者类
        """
        cls._providers[name] = provider_class
        logger.info(f"注册 LLM 提供者: {name}")

    @classmethod
    def list_providers(cls) -> List[str]:
        """列出所有支持的提供者"""
        return list(cls._providers.keys())
