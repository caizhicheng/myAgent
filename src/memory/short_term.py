"""
短期记忆模块
使用 SQLite 存储最近的对话历史
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiosqlite
from loguru import logger


class ShortTermMemory:
    """短期记忆（对话历史）"""

    def __init__(self, db_path: str = "./data/sqlite/memory.db", max_turns: int = 20):
        """
        初始化短期记忆

        Args:
            db_path: 数据库路径
            max_turns: 最大保存轮数
        """
        self.db_path = Path(db_path)
        self.max_turns = max_turns
        self.db: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        """初始化数据库"""
        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # 连接数据库
        self.db = await aiosqlite.connect(self.db_path)

        # 创建表
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        # 创建索引
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_timestamp
            ON conversations(session_id, timestamp)
        """)

        await self.db.commit()
        logger.info(f"短期记忆初始化完成: {self.db_path}")

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ):
        """
        添加消息

        Args:
            session_id: 会话 ID
            role: 角色 (user/assistant/system)
            content: 消息内容
            metadata: 元数据
        """
        if not self.db:
            await self.initialize()

        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

        await self.db.execute(
            """
            INSERT INTO conversations (session_id, role, content, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, metadata_json),
        )

        await self.db.commit()

        # 清理旧消息，保持最大轮数
        await self._cleanup_old_messages(session_id)

    async def get_messages(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[Dict]:
        """
        获取消息列表

        Args:
            session_id: 会话 ID
            limit: 限制数量

        Returns:
            消息列表
        """
        if not self.db:
            await self.initialize()

        limit = limit or self.max_turns

        cursor = await self.db.execute(
            """
            SELECT role, content, timestamp, metadata
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (session_id, limit),
        )

        rows = await cursor.fetchall()

        messages = []
        for row in reversed(rows):  # 反转，保持时间顺序
            metadata = json.loads(row[3]) if row[3] else None
            messages.append(
                {
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "metadata": metadata,
                }
            )

        return messages

    async def get_last_message(self, session_id: str) -> Optional[Dict]:
        """
        获取最后一条消息

        Args:
            session_id: 会话 ID

        Returns:
            最后一条消息
        """
        if not self.db:
            await self.initialize()

        cursor = await self.db.execute(
            """
            SELECT role, content, timestamp, metadata
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (session_id,),
        )

        row = await cursor.fetchone()

        if row:
            metadata = json.loads(row[3]) if row[3] else None
            return {
                "role": row[0],
                "content": row[1],
                "timestamp": row[2],
                "metadata": metadata,
            }

        return None

    async def clear_session(self, session_id: str):
        """
        清空会话

        Args:
            session_id: 会话 ID
        """
        if not self.db:
            await self.initialize()

        await self.db.execute(
            "DELETE FROM conversations WHERE session_id = ?", (session_id,)
        )

        await self.db.commit()
        logger.info(f"已清空会话: {session_id}")

    async def _cleanup_old_messages(self, session_id: str):
        """
        清理旧消息

        Args:
            session_id: 会话 ID
        """
        # 获取当前消息数量
        cursor = await self.db.execute(
            "SELECT COUNT(*) FROM conversations WHERE session_id = ?", (session_id,)
        )

        count = (await cursor.fetchone())[0]

        # 如果超过最大轮数，删除旧消息
        if count > self.max_turns:
            # 获取需要保留的最小 ID
            cursor = await self.db.execute(
                f"""
                SELECT id FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT 1 OFFSET {self.max_turns - 1}
                """,
                (session_id,),
            )

            row = await cursor.fetchone()

            if row:
                min_id = row[0]
                await self.db.execute(
                    "DELETE FROM conversations WHERE session_id = ? AND id < ?",
                    (session_id, min_id),
                )
                await self.db.commit()

    async def search_messages(self, session_id: str, keyword: str) -> List[Dict]:
        """
        搜索消息

        Args:
            session_id: 会话 ID
            keyword: 关键词

        Returns:
            匹配的消息列表
        """
        if not self.db:
            await self.initialize()

        cursor = await self.db.execute(
            """
            SELECT role, content, timestamp, metadata
            FROM conversations
            WHERE session_id = ? AND content LIKE ?
            ORDER BY timestamp DESC
            """,
            (session_id, f"%{keyword}%"),
        )

        rows = await cursor.fetchall()

        messages = []
        for row in rows:
            metadata = json.loads(row[3]) if row[3] else None
            messages.append(
                {
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "metadata": metadata,
                }
            )

        return messages

    async def close(self):
        """关闭数据库连接"""
        if self.db:
            await self.db.close()
            logger.info("短期记忆数据库已关闭")
