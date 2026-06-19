"""
执行命令技能
"""

import asyncio
import platform
from typing import Optional

from loguru import logger

from src.core.config import config
from src.skills.base import Skill, SkillParameter, SkillResult, SkillStatus


class ExecuteCommandSkill(Skill):
    """执行系统命令技能"""

    name = "execute_command"
    description = "执行系统命令（仅限白名单内的命令）"
    category = "system"
    tags = ["system", "command", "shell"]

    parameters = {
        "command": SkillParameter(
            str, "要执行的命令", required=True
        ),
        "timeout": SkillParameter(
            int, "超时时间（秒）", required=False, default=30
        ),
        "cwd": SkillParameter(
            str, "工作目录", required=False, default=None
        ),
    }

    async def execute(
        self,
        command: str,
        timeout: int = 30,
        cwd: Optional[str] = None,
    ) -> SkillResult:
        """
        执行系统命令

        Args:
            command: 命令字符串
            timeout: 超时时间
            cwd: 工作目录

        Returns:
            执行结果
        """
        try:
            # 提取命令名称（第一个词）
            command_name = command.split()[0] if command.split() else ""

            # 检查命令是否在白名单中
            if config.skills.security.whitelist_mode:
                allowed_commands = config.skills.security.allowed_commands

                if command_name not in allowed_commands:
                    return SkillResult(
                        status=SkillStatus.FAILED,
                        output=None,
                        error=f"命令 '{command_name}' 不在白名单中。允许的命令: {', '.join(allowed_commands)}",
                    )

            # 检查超时设置
            max_timeout = config.skills.security.max_command_timeout
            if timeout > max_timeout:
                timeout = max_timeout

            logger.info(f"执行命令: {command}")

            # 根据操作系统选择 shell
            if platform.system() == "Windows":
                # Windows 使用 PowerShell
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    shell=True,
                )
            else:
                # Linux/Mac 使用 bash
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    shell=True,
                )

            try:
                # 等待命令执行完成
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )

                # 解码输出
                stdout_text = stdout.decode("utf-8", errors="ignore")
                stderr_text = stderr.decode("utf-8", errors="ignore")

                # 构建结果
                output = {
                    "command": command,
                    "return_code": process.returncode,
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                }

                if process.returncode == 0:
                    logger.info(f"命令执行成功: {command}")
                    return SkillResult(
                        status=SkillStatus.SUCCESS,
                        output=output,
                        metadata={
                            "timeout": timeout,
                            "cwd": cwd,
                        },
                    )
                else:
                    logger.warning(f"命令执行失败: {command}, 返回码: {process.returncode}")
                    return SkillResult(
                        status=SkillStatus.FAILED,
                        output=output,
                        error=f"命令返回非零状态码: {process.returncode}",
                    )

            except asyncio.TimeoutError:
                # 超时，终止进程
                process.kill()
                await process.wait()

                logger.error(f"命令执行超时: {command}")
                return SkillResult(
                    status=SkillStatus.TIMEOUT,
                    output=None,
                    error=f"命令执行超时（{timeout}秒）",
                )

        except Exception as e:
            logger.error(f"执行命令失败: {command}, {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"执行命令失败: {str(e)}",
            )
