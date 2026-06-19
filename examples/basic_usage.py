"""
示例：基本使用
演示如何使用 Agent 进行对话和执行技能
"""
import sys
import os

# 设置 Windows 控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(sys.path)
import asyncio
from src.agent.runtime import AgentRuntime


async def main():
    """主函数"""
    # 创建 Agent
    agent = AgentRuntime()

    # 初始化
    await agent.initialize()

    print("=" * 50)
    print("MyAgent 基本使用示例")
    print("=" * 50)

    # 示例 1: 简单对话
    print("\n[示例 1] 简单对话")
    print("-" * 50)

    response = await agent.chat("你好！请介绍一下你自己。")
    print(f"用户: 你好！请介绍一下你自己。")
    print(f"Agent: {response}")

    # 示例 2: 执行技能
    print("\n[示例 2] 执行技能")
    print("-" * 50)

    # 列出目录
    result = await agent.execute_skill("list_directory", path=".", pattern="*.py")
    print(f"技能执行结果: {result}")

    # 示例 3: 带技能调用的对话
    print("\n[示例 3] 带技能调用的对话")
    print("-" * 50)

    response = await agent.chat_with_skills("列出当前目录下的所有 Python 文件")
    print(f"用户: 列出当前目录下的所有 Python 文件")
    print(f"Agent: {response}")

    # 示例 4: 多轮对话
    print("\n[示例 4] 多轮对话")
    print("-" * 50)

    await agent.chat("我想了解 Python 的基础知识")
    await agent.chat("能给我推荐一些学习资源吗？")

    history = await agent.get_history(limit=5)
    print(f"对话历史（最近 5 条）:")
    for msg in history:
        print(f"  {msg['role']}: {msg['content'][:50]}...")

    # 关闭 Agent
    await agent.close()
    print("\n" + "=" * 50)
    print("示例完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
