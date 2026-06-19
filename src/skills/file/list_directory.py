"""
列出目录技能
"""

import os
from pathlib import Path
from typing import List, Optional

from loguru import logger

from src.skills.base import Skill, SkillParameter, SkillResult, SkillStatus


class ListDirectorySkill(Skill):
    """列出目录技能"""

    name = "list_directory"
    description = "列出目录内容，支持过滤和排序"
    category = "file"
    tags = ["file", "directory", "list"]

    parameters = {
        "path": SkillParameter(
            str, "目录路径（默认为当前目录）", required=False, default="."
        ),
        "pattern": SkillParameter(
            str, "文件名匹配模式（支持通配符）", required=False, default="*"
        ),
        "show_hidden": SkillParameter(
            bool, "是否显示隐藏文件", required=False, default=False
        ),
        "recursive": SkillParameter(
            bool, "是否递归列出子目录", required=False, default=False
        ),
        "sort_by": SkillParameter(
            str,
            "排序方式（name, size, time）",
            required=False,
            default="name",
            choices=["name", "size", "time"],
        ),
    }

    async def execute(
        self,
        path: str = ".",
        pattern: str = "*",
        show_hidden: bool = False,
        recursive: bool = False,
        sort_by: str = "name",
    ) -> SkillResult:
        """
        执行列出目录

        Args:
            path: 目录路径
            pattern: 匹配模式
            show_hidden: 显示隐藏文件
            recursive: 递归
            sort_by: 排序方式

        Returns:
            执行结果
        """
        try:
            dir_path = Path(path)

            # 检查目录是否存在
            if not dir_path.exists():
                return SkillResult(
                    status=SkillStatus.FAILED,
                    output=None,
                    error=f"目录不存在: {path}",
                )

            # 检查是否为目录
            if not dir_path.is_dir():
                return SkillResult(
                    status=SkillStatus.FAILED,
                    output=None,
                    error=f"路径不是目录: {path}",
                )

            # 获取文件列表
            items = []

            if recursive:
                # 递归模式
                for item in dir_path.rglob(pattern):
                    if not show_hidden and item.name.startswith("."):
                        continue

                    items.append(self._get_item_info(item, dir_path))
            else:
                # 非递归模式
                for item in dir_path.glob(pattern):
                    if not show_hidden and item.name.startswith("."):
                        continue

                    items.append(self._get_item_info(item, dir_path))

            # 排序
            if sort_by == "name":
                items.sort(key=lambda x: x["name"])
            elif sort_by == "size":
                items.sort(key=lambda x: x.get("size", 0), reverse=True)
            elif sort_by == "time":
                items.sort(key=lambda x: x.get("modified", ""), reverse=True)

            logger.info(f"成功列出目录: {path}, 共 {len(items)} 项")

            return SkillResult(
                status=SkillStatus.SUCCESS,
                output=items,
                metadata={
                    "path": str(dir_path.absolute()),
                    "pattern": pattern,
                    "total_items": len(items),
                    "recursive": recursive,
                },
            )

        except PermissionError as e:
            logger.error(f"目录权限不足: {path}, {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"目录权限不足: {str(e)}",
            )

        except Exception as e:
            logger.error(f"列出目录失败: {path}, {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"列出目录失败: {str(e)}",
            )

    def _get_item_info(self, item: Path, base_path: Path) -> dict:
        """
        获取文件/目录信息

        Args:
            item: 文件/目录路径
            base_path: 基础路径

        Returns:
            信息字典
        """
        try:
            stat = item.stat()

            info = {
                "name": item.name,
                "path": str(item.relative_to(base_path)),
                "absolute_path": str(item.absolute()),
                "type": "directory" if item.is_dir() else "file",
                "size": stat.st_size if item.is_file() else None,
                "modified": str(stat.st_mtime),
            }

            # 文件扩展名
            if item.is_file():
                info["extension"] = item.suffix

            return info

        except Exception:
            return {
                "name": item.name,
                "path": str(item.relative_to(base_path)),
                "type": "unknown",
                "error": "无法获取信息",
            }
