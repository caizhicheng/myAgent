"""
搜索文件技能
"""

import fnmatch
from pathlib import Path
from typing import List, Optional

from loguru import logger

from src.skills.base import Skill, SkillParameter, SkillResult, SkillStatus


class SearchFilesSkill(Skill):
    """搜索文件技能"""

    name = "search_files"
    description = "搜索文件和目录，支持文件名和内容搜索"
    category = "file"
    tags = ["file", "search", "find"]

    parameters = {
        "path": SkillParameter(
            str, "搜索起始目录", required=False, default="."
        ),
        "pattern": SkillParameter(
            str, "文件名匹配模式（支持通配符）", required=False, default="*"
        ),
        "content": SkillParameter(
            str, "搜索文件内容（可选）", required=False, default=None
        ),
        "file_type": SkillParameter(
            str, "文件类型过滤（如 .py, .txt）", required=False, default=None
        ),
        "max_results": SkillParameter(
            int, "最大结果数量", required=False, default=100
        ),
    }

    async def execute(
        self,
        path: str = ".",
        pattern: str = "*",
        content: Optional[str] = None,
        file_type: Optional[str] = None,
        max_results: int = 100,
    ) -> SkillResult:
        """
        执行搜索文件

        Args:
            path: 搜索目录
            pattern: 文件名模式
            content: 内容关键词
            file_type: 文件类型
            max_results: 最大结果数

        Returns:
            执行结果
        """
        try:
            search_path = Path(path)

            # 检查目录是否存在
            if not search_path.exists():
                return SkillResult(
                    status=SkillStatus.FAILED,
                    output=None,
                    error=f"目录不存在: {path}",
                )

            # 搜索文件
            results = []

            # 递归搜索
            for item in search_path.rglob(pattern):
                # 限制结果数量
                if len(results) >= max_results:
                    break

                # 文件类型过滤
                if file_type and item.suffix != file_type:
                    continue

                # 只搜索文件
                if not item.is_file():
                    continue

                # 内容搜索
                if content:
                    try:
                        with open(item, "r", encoding="utf-8", errors="ignore") as f:
                            file_content = f.read()

                        if content.lower() in file_content.lower():
                            # 找到匹配的内容
                            matches = self._find_content_matches(
                                file_content, content, max_matches=3
                            )

                            results.append(
                                {
                                    "path": str(item.relative_to(search_path)),
                                    "absolute_path": str(item.absolute()),
                                    "size": item.stat().st_size,
                                    "matches": matches,
                                }
                            )

                    except Exception:
                        # 跳过无法读取的文件
                        continue
                else:
                    # 只搜索文件名
                    results.append(
                        {
                            "path": str(item.relative_to(search_path)),
                            "absolute_path": str(item.absolute()),
                            "size": item.stat().st_size,
                        }
                    )

            logger.info(f"搜索完成: {path}, 找到 {len(results)} 个结果")

            return SkillResult(
                status=SkillStatus.SUCCESS,
                output=results,
                metadata={
                    "search_path": str(search_path.absolute()),
                    "pattern": pattern,
                    "content": content,
                    "file_type": file_type,
                    "total_results": len(results),
                },
            )

        except Exception as e:
            logger.error(f"搜索文件失败: {path}, {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"搜索文件失败: {str(e)}",
            )

    def _find_content_matches(
        self, content: str, keyword: str, max_matches: int = 3
    ) -> List[dict]:
        """
        查找内容匹配

        Args:
            content: 文件内容
            keyword: 关键词
            max_matches: 最大匹配数

        Returns:
            匹配列表
        """
        matches = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                # 找到匹配的行
                start = max(0, i - 2)
                end = min(len(lines), i + 3)

                context = "\n".join(lines[start:end])

                matches.append(
                    {
                        "line_number": i + 1,
                        "context": context,
                    }
                )

                if len(matches) >= max_matches:
                    break

        return matches
