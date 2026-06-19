"""
示例：技能使用
演示如何使用各种技能
"""

import asyncio
from src.skills.manager import SkillManager


async def main():
    """主函数"""
    # 创建技能管理器
    manager = SkillManager()

    # 初始化
    await manager.initialize()

    print("=" * 50)
    print("技能使用示例")
    print("=" * 50)

    # 列出所有技能
    print("\n[可用技能列表]")
    print("-" * 50)

    skills = manager.list_skills()
    for skill in skills:
        print(f"- {skill['name']}: {skill['description']}")

    # 示例 1: 文件操作
    print("\n[示例 1] 文件操作")
    print("-" * 50)

    # 写入文件
    result = await manager.execute_skill(
        "write_file",
        path="./data/example/test.txt",
        content="这是一个测试文件\n第二行内容\n第三行内容",
    )
    print(f"写入文件: {result.output}")

    # 读取文件
    result = await manager.execute_skill(
        "read_file",
        path="./data/example/test.txt",
        lines=2,
    )
    print(f"读取文件（前 2 行）:\n{result.output}")

    # 列出目录
    result = await manager.execute_skill(
        "list_directory",
        path="./data/example",
        pattern="*",
    )
    print(f"\n目录内容:")
    for item in result.output:
        print(f"  - {item['name']} ({item['type']})")

    # 示例 2: 系统信息
    print("\n[示例 2] 系统信息")
    print("-" * 50)

    result = await manager.execute_skill("get_system_info", detail=False)
    info = result.output

    print(f"系统: {info['system']['system']} {info['system']['release']}")
    print(f"CPU 使用率: {info['cpu']['percent']}%")
    print(f"内存使用率: {info['memory']['percent']}%")

    # 示例 3: 进程管理
    print("\n[示例 3] 进程管理")
    print("-" * 50)

    result = await manager.execute_skill(
        "list_processes",
        sort_by="memory",
        limit=5,
    )

    print("内存占用最高的 5 个进程:")
    for proc in result.output:
        print(f"  - {proc['name']} (PID: {proc['pid']}, 内存: {proc['memory_percent']:.2f}%)")

    # 示例 4: 搜索文件
    print("\n[示例 4] 搜索文件")
    print("-" * 50)

    result = await manager.execute_skill(
        "search_files",
        path=".",
        pattern="*.py",
        file_type=".py",
        max_results=5,
    )

    print("找到的 Python 文件:")
    for file in result.output:
        print(f"  - {file['path']}")

    print("\n" + "=" * 50)
    print("示例完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
