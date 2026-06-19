"""
技能管理器
负责技能的注册、发现和执行
"""

import importlib
import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from loguru import logger

from src.core.config import config
from src.skills.base import Skill, SkillResult


class SkillManager:
    """技能管理器"""

    def __init__(self):
        """初始化技能管理器"""
        self.skills: Dict[str, Skill] = {}
        self._initialized = False

    async def initialize(self):
        """初始化技能管理器"""
        if self._initialized:
            return

        # 自动加载技能
        if config.skills.auto_load:
            await self.auto_load_skills()

        self._initialized = True
        logger.info(f"技能管理器初始化完成，已加载 {len(self.skills)} 个技能")

    def register_skill(self, skill_class: Type[Skill]):
        """
        注册技能

        Args:
            skill_class: 技能类
        """
        skill = skill_class()
        self.skills[skill.name] = skill
        logger.info(f"注册技能: {skill.name} ({skill.description})")

    def unregister_skill(self, skill_name: str):
        """
        注销技能

        Args:
            skill_name: 技能名称
        """
        if skill_name in self.skills:
            del self.skills[skill_name]
            logger.info(f"注销技能: {skill_name}")

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """
        获取技能

        Args:
            skill_name: 技能名称

        Returns:
            技能实例
        """
        return self.skills.get(skill_name)

    def list_skills(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有技能

        Args:
            category: 分类过滤

        Returns:
            技能信息列表
        """
        skills_info = []

        for skill in self.skills.values():
            if category and skill.category != category:
                continue

            skills_info.append(skill.get_info())

        return skills_info

    async def execute_skill(self, skill_name: str, **kwargs) -> SkillResult:
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

        skill = self.get_skill(skill_name)

        if not skill:
            return SkillResult(
                status="failed",
                output=None,
                error=f"技能不存在: {skill_name}",
            )

        # 验证参数
        errors = skill.validate_parameters(kwargs)
        if errors:
            return SkillResult(
                status="failed",
                output=None,
                error=f"参数验证失败: {'; '.join(errors)}",
            )

        try:
            logger.info(f"执行技能: {skill_name}, 参数: {kwargs}")
            result = await skill.execute(**kwargs)
            logger.info(f"技能执行完成: {skill_name}, 状态: {result.status}")
            return result

        except Exception as e:
            logger.error(f"技能执行失败: {skill_name}, 错误: {e}")
            return SkillResult(
                status="failed",
                output=None,
                error=f"执行失败: {str(e)}",
            )

    async def auto_load_skills(self):
        """自动加载技能"""
        skill_dirs = config.skills.skill_dirs

        for skill_dir in skill_dirs:
            skill_path = Path(skill_dir)

            if not skill_path.exists():
                logger.warning(f"技能目录不存在: {skill_dir}")
                continue

            await self._load_skills_from_directory(skill_path)

    async def _load_skills_from_directory(self, directory: Path):
        """
        从目录加载技能

        Args:
            directory: 目录路径
        """
        logger.info(f"从目录加载技能: {directory}")

        # 查找所有 Python 文件
        for file_path in directory.glob("**/*.py"):
            if file_path.name.startswith("_"):
                continue

            try:
                # 动态导入模块
                module_name = str(file_path.with_suffix("")).replace("\\", ".").replace("/", ".")
                spec = importlib.util.spec_from_file_location(module_name, file_path)

                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # 查找所有 Skill 子类
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, Skill)
                            and obj != Skill
                        ):
                            try:
                                self.register_skill(obj)
                            except Exception as e:
                                logger.error(f"注册技能失败 {name}: {e}")

            except Exception as e:
                logger.error(f"加载技能文件失败 {file_path}: {e}")

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        获取所有技能的工具 Schema

        Returns:
            工具 Schema 列表
        """
        return [skill.to_tool_schema() for skill in self.skills.values()]

    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        获取技能信息

        Args:
            skill_name: 技能名称

        Returns:
            技能信息字典
        """
        skill = self.get_skill(skill_name)
        return skill.get_info() if skill else None
