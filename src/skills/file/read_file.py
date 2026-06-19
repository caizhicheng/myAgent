"""
读取文件技能
"""

from pathlib import Path
from typing import Optional

from loguru import logger

from src.skills.base import Skill, SkillParameter, SkillResult, SkillStatus


class ReadFileSkill(Skill):
    """读取文件技能"""

    name = "read_file"
    description = "读取文件内容，支持指定编码和行数限制"
    category = "file"
    tags = ["file", "read", "io"]

    parameters = {
        "path": SkillParameter(
            str, "文件路径（绝对路径或相对路径）", required=True
        ),
        "encoding": SkillParameter(
            str, "文件编码", required=False, default="utf-8"
        ),
        "lines": SkillParameter(
            int, "读取行数（-1 表示读取全部）", required=False, default=-1
        ),
        "offset": SkillParameter(
            int, "起始行号（从 0 开始）", required=False, default=0
        ),
    }

    async def execute(
        self,
        path: str,
        encoding: str = "utf-8",
        lines: int = -1,
        offset: int = 0,
    ) -> SkillResult:
        """
        执行读取文件

        Args:
            path: 文件路径
            encoding: 文件编码
            lines: 读取行数
            offset: 起始行号

        Returns:
            执行结果
        """
        try:
            file_path = Path(path)

            # 检查文件是否存在
            if not file_path.exists():
                return SkillResult(
                    status=SkillStatus.FAILED,
                    output=None,
                    error=f"文件不存在: {path}",
                )

            # 检查是否为文件
            if not file_path.is_file():
                return SkillResult(
                    status=SkillStatus.FAILED,
                    output=None,
                    error=f"路径不是文件: {path}",
                )

            # 读取文件
            with open(file_path, "r", encoding=encoding) as f:
                if lines == -1:
                    # 读取全部内容
                    content = f.read()
                else:
                    # 读取指定行数
                    all_lines = f.readlines()
                    selected_lines = all_lines[offset : offset + lines]
                    content = "".join(selected_lines)

            logger.info(f"成功读取文件: {path}")

            return SkillResult(
                status=SkillStatus.SUCCESS,
                output=content,
                metadata={
                    "path": str(file_path.absolute()),
                    "encoding": encoding,
                    "lines": lines,
                    "offset": offset,
                    "size": len(content),
                },
            )

        except UnicodeDecodeError as e:
            logger.error(f"文件编码错误: {path}, {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"文件编码错误: {str(e)}",
            )

        except PermissionError as e:
            logger.error(f"文件权限不足: {path}, {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"文件权限不足: {str(e)}",
            )

        except Exception as e:
            logger.error(f"读取文件失败: {path}, {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"读取文件失败: {str(e)}",
            )
