"""
提示工程模块
管理 Agent 的提示模板
"""

from typing import Dict, List, Optional
from string import Template

from loguru import logger


class PromptTemplate:
    """提示模板"""

    def __init__(self, template: str, name: str = ""):
        """
        初始化提示模板

        Args:
            template: 模板字符串
            name: 模板名称
        """
        self.template = template
        self.name = name

    def render(self, **kwargs) -> str:
        """
        渲染模板

        Args:
            **kwargs: 模板变量

        Returns:
            渲染后的字符串
        """
        try:
            return Template(self.template).safe_substitute(**kwargs)
        except Exception as e:
            logger.error(f"模板渲染失败: {e}")
            return self.template


class PromptManager:
    """提示管理器"""

    def __init__(self):
        """初始化提示管理器"""
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """加载默认模板"""
        # 系统提示模板
        self.register_template(
            "system",
            """你是一个智能助手 ${agent_name}。

你的职责是帮助用户完成各种任务。你具备以下能力：
- 回答问题和提供建议
- 执行文件操作（读取、写入、搜索）
- 执行系统命令
- 获取系统信息
- 管理进程

重要规则：
1. 在执行任何操作前，请先确认用户意图
2. 对于危险操作（如删除文件），必须征得用户同意
3. 提供清晰、准确的回复
4. 遇到错误时，给出友好的错误提示和解决建议

当前时间：${current_time}
系统：${system_info}
""",
        )

        # 技能调用提示模板
        self.register_template(
            "skill_invocation",
            """用户请求：${user_request}

可用技能：
${available_skills}

请分析用户请求，判断是否需要调用技能。如果需要，请提供：
1. 技能名称
2. 所需参数
3. 调用理由
""",
        )

        # 错误处理提示模板
        self.register_template(
            "error_handling",
            """执行过程中发生错误：

错误信息：${error_message}
错误类型：${error_type}

请分析错误原因，并提供解决方案。
""",
        )

        # 对话总结提示模板
        self.register_template(
            "conversation_summary",
            """请总结以下对话内容：

${conversation_history}

要求：
1. 提取关键信息
2. 列出重要决策
3. 记录待办事项
""",
        )

        logger.info("默认提示模板加载完成")

    def register_template(self, name: str, template: str):
        """
        注册模板

        Args:
            name: 模板名称
            template: 模板字符串
        """
        self.templates[name] = PromptTemplate(template, name)
        logger.debug(f"注册提示模板: {name}")

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        获取模板

        Args:
            name: 模板名称

        Returns:
            模板对象
        """
        return self.templates.get(name)

    def render(self, name: str, **kwargs) -> str:
        """
        渲染模板

        Args:
            name: 模板名称
            **kwargs: 模板变量

        Returns:
            渲染后的字符串
        """
        template = self.get_template(name)

        if not template:
            logger.warning(f"模板不存在: {name}")
            return ""

        return template.render(**kwargs)

    def build_system_prompt(
        self,
        agent_name: str,
        current_time: str,
        system_info: str,
    ) -> str:
        """
        构建系统提示

        Args:
            agent_name: Agent 名称
            current_time: 当前时间
            system_info: 系统信息

        Returns:
            系统提示字符串
        """
        return self.render(
            "system",
            agent_name=agent_name,
            current_time=current_time,
            system_info=system_info,
        )

    def build_skill_invocation_prompt(
        self, user_request: str, available_skills: List[Dict]
    ) -> str:
        """
        构建技能调用提示

        Args:
            user_request: 用户请求
            available_skills: 可用技能列表

        Returns:
            技能调用提示字符串
        """
        # 格式化技能列表
        skills_text = "\n".join(
            [
                f"- {skill['name']}: {skill['description']}"
                for skill in available_skills
            ]
        )

        return self.render(
            "skill_invocation",
            user_request=user_request,
            available_skills=skills_text,
        )

    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.templates.keys())
