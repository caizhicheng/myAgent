"""
技能系统测试
"""

import pytest
from src.skills.manager import SkillManager
from src.skills.file.read_file import ReadFileSkill
from src.skills.file.write_file import WriteFileSkill


@pytest.mark.asyncio
async def test_skill_manager():
    """测试技能管理器"""
    manager = SkillManager()

    # 初始化
    await manager.initialize()

    # 检查技能加载
    skills = manager.list_skills()
    assert len(skills) > 0

    # 检查技能信息
    skill_info = manager.get_skill_info("read_file")
    assert skill_info is not None
    assert skill_info["name"] == "read_file"


@pytest.mark.asyncio
async def test_file_skills():
    """测试文件技能"""
    manager = SkillManager()
    await manager.initialize()

    # 测试写入文件
    result = await manager.execute_skill(
        "write_file",
        path="./data/test/test_file.txt",
        content="测试内容",
        mode="write",
    )

    assert result.is_success()

    # 测试读取文件
    result = await manager.execute_skill(
        "read_file",
        path="./data/test/test_file.txt",
    )

    assert result.is_success()
    assert result.output == "测试内容"


@pytest.mark.asyncio
async def test_list_directory_skill():
    """测试列出目录技能"""
    manager = SkillManager()
    await manager.initialize()

    # 列出当前目录
    result = await manager.execute_skill(
        "list_directory",
        path=".",
        pattern="*.py",
    )

    assert result.is_success()
    assert isinstance(result.output, list)


@pytest.mark.asyncio
async def test_search_files_skill():
    """测试搜索文件技能"""
    manager = SkillManager()
    await manager.initialize()

    # 搜索 Python 文件
    result = await manager.execute_skill(
        "search_files",
        path=".",
        pattern="*.py",
        file_type=".py",
        max_results=10,
    )

    assert result.is_success()
    assert isinstance(result.output, list)
