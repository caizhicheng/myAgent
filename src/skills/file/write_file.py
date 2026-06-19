"""
写入文件技能
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

from src.skills.base import Skill, SkillParameter, SkillResult, SkillStatus


class WriteFileSkill(Skill):
    """写入文件技能"""

    name = "write_file"
    description = "写入内容到文件，支持自动创建目录和备份"
    category = "file"
    tags = ["file", "write", "io"]

    parameters = {
        "path": SkillParameter(
            str, "文件路径（绝对路径或相对路径）", required=True
        ),
        "content": SkillParameter(
            str, "要写入的内容", required=True
        ),
        "mode": SkillParameter(
            str,
            "写入模式（write: 覆盖，append: 追加）",
            required=False,
            default="write",
            choices=["write", "append"],
        ),
        "encoding": SkillParameter(
            str, "文件编码", required=False, default="utf-8"
        ),
        "backup": SkillParameter(
            bool, "是否备份原文件", required=False, default=True
        ),
    }

    async def execute(
        self,
        path: str,
        content: str,
        mode: str = "write",
        encoding: str = "utf-8",
        backup: bool = True,
    ) -> SkillResult:
        """
        执行写入文件

        Args:
            path: 文件路径
            content: 写入内容
            mode: 写入模式
            encoding: 文件编码
            backup: 是否备份

        Returns:
            执行结果
        """
        try:
            file_path = Path(path)

            # 创建父目录
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 备份原文件
            backup_path = None
            if backup and file_path.exists() and mode == "write":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = file_path.with_suffix(f".backup_{timestamp}{file_path.suffix}")
                shutil.copy2(file_path, backup_path)
                logger.info(f"已备份原文件到: {backup_path}")

            # 写入文件
            write_mode = "w" if mode == "write" else "a"

            with open(file_path, write_mode, encoding=encoding) as f:
                f.write(content)

            logger.info(f"成功写入文件: {path}")

            return SkillResult(
                status=SkillStatus.SUCCESS,
                output=f"成功写入文件: {path}",
                metadata={
                    "path": str(file_path.absolute()),
                    "mode": mode,
                    "encoding": encoding,
                    "size": len(content),
                    "backup_path": str(backup_path) if backup_path else None,
                },
            )

        except PermissionError as e:
            logger.error(f"文件权限不足: {path}, {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"文件权限不足: {str(e)}",
            )

        except Exception as e:
            logger.error(f"写入文件失败: {path}, {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"写入文件失败: {str(e)}",
            )
