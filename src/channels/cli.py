"""
CLI 交互通道
提供命令行交互界面
"""

import asyncio
from pathlib import Path
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from loguru import logger

from src.agent.runtime import AgentRuntime
from src.channels.base import Channel
from src.core.config import config


class CLIChannel(Channel):
    """命令行交互通道"""

    def __init__(self, agent: Optional[AgentRuntime] = None):
        """
        初始化 CLI 通道

        Args:
            agent: Agent 实例
        """
        self.agent = agent or AgentRuntime()
        self.console = Console()
        self.session: Optional[PromptSession] = None
        self.running = False

        # 自定义样式
        self.style = Style.from_dict(
            {
                "prompt": "bold cyan",
            }
        )

    async def start(self):
        """启动 CLI 交互"""
        # 初始化 Agent
        await self.agent.initialize()

        # 初始化 Prompt Session
        history_file = Path(config.channels.cli.history_file)
        history_file.parent.mkdir(parents=True, exist_ok=True)

        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            style=self.style,
        )

        self.running = True

        # 显示欢迎信息
        self._show_welcome()

        # 主循环
        await self._main_loop()

    async def stop(self):
        """停止 CLI 交互"""
        self.running = False
        await self.agent.close()
        self.console.print("\n[bold green]再见！[/bold green]")

    async def send_message(self, message: str):
        """
        发送消息（由 Agent 调用）

        Args:
            message: 消息内容
        """
        self._print_response(message)

    def _show_welcome(self):
        """显示欢迎信息"""
        welcome_text = f"""
# {config.agent.name} v{config.agent.version}

{config.agent.description}

**可用命令：**
- `/help` - 显示帮助信息
- `/clear` - 清空对话历史
- `/history` - 查看对话历史
- `/skills` - 列出所有技能
- `/config` - 查看配置
- `/quit` 或 `/exit` - 退出程序

**提示：** 直接输入消息即可与 Agent 对话！
        """

        self.console.print(Panel(Markdown(welcome_text), border_style="cyan"))
        self.console.print()

    async def _main_loop(self):
        """主循环"""
        while self.running:
            try:
                # 获取用户输入
                user_input = await self.session.prompt_async(
                    f"{config.channels.cli.prompt_style} ",
                )

                # 处理输入
                if not user_input.strip():
                    continue

                # 检查是否为命令
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                else:
                    # 普通对话
                    await self._handle_chat(user_input)

            except KeyboardInterrupt:
                # Ctrl+C
                self.console.print("\n[yellow]使用 /quit 退出程序[/yellow]")

            except EOFError:
                # Ctrl+D
                await self.stop()
                break

            except Exception as e:
                logger.error(f"处理输入失败: {e}")
                self.console.print(f"[red]错误: {str(e)}[/red]")

    async def _handle_command(self, command: str):
        """
        处理命令

        Args:
            command: 命令字符串
        """
        cmd = command.strip().lower()

        if cmd in ["/quit", "/exit"]:
            await self.stop()

        elif cmd == "/help":
            self._show_help()

        elif cmd == "/clear":
            await self.agent.clear_history()
            self.console.print("[green]对话历史已清空[/green]")

        elif cmd == "/history":
            await self._show_history()

        elif cmd == "/skills":
            await self._show_skills()

        elif cmd == "/config":
            self._show_config()

        else:
            self.console.print(f"[yellow]未知命令: {command}[/yellow]")
            self.console.print("[yellow]输入 /help 查看可用命令[/yellow]")

    async def _handle_chat(self, message: str):
        """
        处理对话

        Args:
            message: 用户消息
        """
        try:
            # 显示思考提示
            with self.console.status("[bold cyan]思考中...[/bold cyan]"):
                # 调用 Agent
                response = await self.agent.chat_with_skills(message)

            # 显示回复
            self._print_response(response)

        except Exception as e:
            logger.error(f"对话失败: {e}")
            self.console.print(f"[red]对话失败: {str(e)}[/red]")

    def _print_response(self, response: str):
        """
        打印回复

        Args:
            response: 回复内容
        """
        # 检测是否包含代码块
        if "```" in response:
            # 使用 Markdown 渲染
            self.console.print("\n[bold green]Agent:[/bold green]")
            self.console.print(Markdown(response))
        else:
            # 普通文本
            self.console.print(f"\n[bold green]Agent:[/bold green] {response}")

        self.console.print()

    def _show_help(self):
        """显示帮助信息"""
        help_text = """
**命令列表：**

- `/help` - 显示帮助信息
- `/clear` - 清空对话历史
- `/history` - 查看对话历史
- `/skills` - 列出所有技能
- `/config` - 查看配置
- `/quit` 或 `/exit` - 退出程序

**使用技巧：**

1. 直接输入问题，Agent 会自动判断是否需要调用技能
2. 可以使用自然语言描述任务，如"读取 README.md 文件"
3. Agent 会记住对话上下文，可以进行多轮对话
        """

        self.console.print(Panel(Markdown(help_text), title="帮助", border_style="green"))
        self.console.print()

    async def _show_history(self):
        """显示对话历史"""
        history = await self.agent.get_history(limit=10)

        if not history:
            self.console.print("[yellow]暂无对话历史[/yellow]")
            return

        self.console.print("\n[bold cyan]对话历史：[/bold cyan]")

        for msg in history:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                self.console.print(f"[bold blue]用户:[/bold blue] {content}")
            elif role == "assistant":
                self.console.print(f"[bold green]Agent:[/bold green] {content[:100]}...")

        self.console.print()

    async def _show_skills(self):
        """显示技能列表"""
        skills = self.agent.skills.list_skills()

        if not skills:
            self.console.print("[yellow]暂无可用技能[/yellow]")
            return

        self.console.print("\n[bold cyan]可用技能：[/bold cyan]\n")

        for skill in skills:
            self.console.print(f"[bold]{skill['name']}[/bold]")
            self.console.print(f"  描述: {skill['description']}")
            self.console.print(f"  分类: {skill['category']}")
            self.console.print(f"  标签: {', '.join(skill['tags'])}")
            self.console.print()

    def _show_config(self):
        """显示配置信息"""
        config_text = f"""
**Agent 配置：**
- 名称: {config.agent.name}
- 版本: {config.agent.version}
- 描述: {config.agent.description}

**LLM 配置：**
- 提供者: {config.settings.llm_provider}
- 模型: {config.get_llm_config().get('model')}

**记忆配置：**
- 短期记忆: {'启用' if config.memory.short_term.enabled else '禁用'}
- 长期记忆: {'启用' if config.memory.long_term.enabled else '禁用'}
- 最大轮数: {config.memory.short_term.max_turns}

**技能配置：**
- 技能数量: {len(self.agent.skills.skills)}
- 白名单模式: {'启用' if config.skills.security.whitelist_mode else '禁用'}
        """

        self.console.print(Panel(Markdown(config_text), title="配置", border_style="yellow"))
        self.console.print()
