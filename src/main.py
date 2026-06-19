"""
主程序入口
"""

import asyncio
import sys

from loguru import logger

from src.agent.runtime import AgentRuntime
from src.channels.cli import CLIChannel


async def main():
    """主函数"""
    try:
        # 创建 Agent
        agent = AgentRuntime()

        # 创建 CLI 通道
        cli = CLIChannel(agent)

        # 启动 CLI
        await cli.start()

    except KeyboardInterrupt:
        logger.info("用户中断程序")

    except Exception as e:
        logger.error(f"程序异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
