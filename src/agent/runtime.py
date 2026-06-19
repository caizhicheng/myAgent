"""
Agent 运行时
核心 Agent 引擎，负责对话管理和技能调用
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncIterator

from loguru import logger

from src.core.config import config
from src.core.llm import LLMFactory, Message
from src.memory.manager import MemoryManager
from src.skills.manager import SkillManager
from src.agent.prompt import PromptManager


class AgentRuntime:
    """Agent 运行时"""

    def __init__(self):
        """初始化 Agent 运行时"""
        self.config = config
        self.llm = None
        self.memory = MemoryManager()
        self.skills = SkillManager()
        self.prompts = PromptManager()
        self.session_id = "default"
        self._initialized = False

    async def initialize(self):
        """初始化 Agent"""
        if self._initialized:
            return

        # 初始化 LLM
        llm_config = self.config.get_llm_config()
        self.llm = LLMFactory.create(llm_config["provider"], llm_config)

        # 初始化记忆系统
        await self.memory.initialize()

        # 初始化技能系统
        await self.skills.initialize()

        self._initialized = True
        logger.info("Agent 运行时初始化完成")

    async def chat(self, message: str) -> str:
        """
        对话（非流式）

        Args:
            message: 用户消息

        Returns:
            Agent 回复
        """
        if not self._initialized:
            await self.initialize()

        try:
            # 添加用户消息到记忆
            await self.memory.add_message(
                self.session_id, "user", message
            )

            # 获取对话历史
            history = await self.memory.get_conversation_history(self.session_id)

            # 构建消息列表
            messages = await self._build_messages(history)

            # 调用 LLM
            response = await self.llm.chat(messages)

            # 添加助手消息到记忆
            await self.memory.add_message(
                self.session_id, "assistant", response
            )

            return response

        except Exception as e:
            logger.error(f"对话失败: {e}")
            error_msg = f"抱歉，处理您的请求时发生错误: {str(e)}"
            await self.memory.add_message(self.session_id, "assistant", error_msg)
            return error_msg

    async def stream_chat(self, message: str):
        """
        流式对话

        Args:
            message: 用户消息

        Yields:
            Agent 回复片段
        """
        if not self._initialized:
            await self.initialize()

        try:
            # 添加用户消息到记忆
            await self.memory.add_message(
                self.session_id, "user", message
            )

            # 获取对话历史
            history = await self.memory.get_conversation_history(self.session_id)

            # 构建消息列表
            messages = await self._build_messages(history)

            # 流式输出
            response_text = ""
            async for chunk in self.llm.stream_chat(messages):
                response_text += chunk
                yield chunk

            # 保存完整回复
            await self.memory.add_message(
                self.session_id, "assistant", response_text
            )

        except Exception as e:
            logger.error(f"对话失败: {e}")
            error_msg = f"抱歉，处理您的请求时发生错误: {str(e)}"
            await self.memory.add_message(self.session_id, "assistant", error_msg)
            yield error_msg

    async def chat_with_skills(self, message: str) -> str:
        """
        带技能调用的对话

        Args:
            message: 用户消息

        Returns:
            Agent 回复
        """
        if not self._initialized:
            await self.initialize()

        try:
            # 添加用户消息到记忆
            await self.memory.add_message(self.session_id, "user", message)

            # 获取对话历史
            history = await self.memory.get_conversation_history(self.session_id)

            # 构建消息列表
            messages = await self._build_messages(history)

            # 获取工具 Schema
            tools = self.skills.get_tools_schema()

            # 调用 LLM（带工具）
            result = await self.llm.chat_with_tools(messages, tools)

            # 检查是否有工具调用
            if result.get("tool_calls"):
                # 执行工具调用
                tool_results = await self._execute_tool_calls(result["tool_calls"])

                # 将工具结果添加到消息
                messages.append(
                    Message(
                        role="assistant",
                        content=result.get("content", ""),
                    )
                )

                # 添加工具结果消息
                for tool_call in result["tool_calls"]:
                    tool_name = tool_call.get("name")
                    tool_result = tool_results.get(tool_name, {})

                    messages.append(
                        Message(
                            role="user",
                            content=f"工具 {tool_name} 执行结果:\n{json.dumps(tool_result, ensure_ascii=False, indent=2)}",
                        )
                    )

                # 再次调用 LLM 生成最终回复
                final_response = await self.llm.chat(messages)

                # 保存回复
                await self.memory.add_message(
                    self.session_id, "assistant", final_response
                )

                return final_response
            else:
                # 没有工具调用，直接返回回复
                response = result.get("content", "")

                await self.memory.add_message(
                    self.session_id, "assistant", response
                )

                return response

        except Exception as e:
            logger.error(f"对话失败: {e}")
            error_msg = f"抱歉，处理您的请求时发生错误: {str(e)}"
            await self.memory.add_message(self.session_id, "assistant", error_msg)
            return error_msg

    async def execute_skill(self, skill_name: str, **kwargs) -> Dict[str, Any]:
        """
        执行技能

        Args:
            skill_name: 技能名称
            **kwargs: 技能参数

        Returns:
            执行结果
        """
        if not self._initialized:
            await self.initialize()

        result = await self.skills.execute_skill(skill_name, **kwargs)
        return result.to_dict()

    async def _build_messages(self, history: List[Dict]) -> List[Message]:
        """
        构建消息列表

        Args:
            history: 对话历史

        Returns:
            消息列表
        """
        messages = []

        # 添加系统提示
        system_prompt = self.prompts.build_system_prompt(
            agent_name=self.config.agent.name,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            system_info=f"{self.config.agent.description}",
        )

        messages.append(Message(role="system", content=system_prompt))

        # 添加对话历史
        for msg in history:
            messages.append(
                Message(role=msg["role"], content=msg["content"])
            )

        return messages

    async def _execute_tool_calls(self, tool_calls: List[Dict]) -> Dict[str, Any]:
        """
        执行工具调用

        Args:
            tool_calls: 工具调用列表

        Returns:
            工具执行结果
        """
        results = {}

        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})

            logger.info(f"执行工具: {tool_name}, 参数: {tool_args}")

            # 执行技能
            result = await self.skills.execute_skill(tool_name, **tool_args)

            results[tool_name] = result.to_dict()

        return results

    async def clear_history(self):
        """清空对话历史"""
        await self.memory.clear_conversation(self.session_id)
        logger.info(f"已清空会话历史: {self.session_id}")

    async def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取对话历史

        Args:
            limit: 限制数量

        Returns:
            对话历史列表
        """
        return await self.memory.get_conversation_history(self.session_id, limit)

    def set_session(self, session_id: str):
        """
        设置会话 ID

        Args:
            session_id: 会话 ID
        """
        self.session_id = session_id
        logger.info(f"切换到会话: {session_id}")

    async def close(self):
        """关闭 Agent"""
        await self.memory.close()
        logger.info("Agent 运行时已关闭")
