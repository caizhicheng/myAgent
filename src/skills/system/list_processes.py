"""
列出进程技能
"""

import psutil
from typing import Optional

from loguru import logger

from src.skills.base import Skill, SkillParameter, SkillResult, SkillStatus


class ListProcessesSkill(Skill):
    """列出运行中的进程"""

    name = "list_processes"
    description = "列出运行中的进程，支持过滤和排序"
    category = "system"
    tags = ["system", "process", "monitor"]

    parameters = {
        "name": SkillParameter(
            str, "进程名称过滤（可选）", required=False, default=None
        ),
        "sort_by": SkillParameter(
            str,
            "排序方式（cpu, memory, name）",
            required=False,
            default="memory",
            choices=["cpu", "memory", "name"],
        ),
        "limit": SkillParameter(
            int, "返回数量限制", required=False, default=20
        ),
    }

    async def execute(
        self,
        name: Optional[str] = None,
        sort_by: str = "memory",
        limit: int = 20,
    ) -> SkillResult:
        """
        列出进程

        Args:
            name: 进程名称过滤
            sort_by: 排序方式
            limit: 数量限制

        Returns:
            执行结果
        """
        try:
            processes = []

            # 遍历所有进程
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent", "status", "username"]
            ):
                try:
                    proc_info = proc.info

                    # 名称过滤
                    if name and name.lower() not in proc_info["name"].lower():
                        continue

                    processes.append(
                        {
                            "pid": proc_info["pid"],
                            "name": proc_info["name"],
                            "cpu_percent": proc_info["cpu_percent"] or 0.0,
                            "memory_percent": round(proc_info["memory_percent"] or 0.0, 2),
                            "status": proc_info["status"],
                            "username": proc_info["username"],
                        }
                    )

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # 排序
            if sort_by == "cpu":
                processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda x: x["memory_percent"], reverse=True)
            elif sort_by == "name":
                processes.sort(key=lambda x: x["name"])

            # 限制数量
            processes = processes[:limit]

            logger.info(f"成功列出进程，共 {len(processes)} 个")

            return SkillResult(
                status=SkillStatus.SUCCESS,
                output=processes,
                metadata={
                    "name_filter": name,
                    "sort_by": sort_by,
                    "limit": limit,
                    "total": len(processes),
                },
            )

        except Exception as e:
            logger.error(f"列出进程失败: {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"列出进程失败: {str(e)}",
            )
