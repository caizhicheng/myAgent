"""
长期记忆模块
使用 SQLite 存储持久化的知识和重要信息
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite
from loguru import logger


class LongTermMemory:
    """长期记忆（知识库）"""

    def __init__(self, db_path: str = "./data/sqlite/knowledge.db"):
        """
        初始化长期记忆

        Args:
            db_path: 数据库路径
        """
        self.db_path = Path(db_path)
        self.db: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        """初始化数据库"""
        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # 连接数据库
        self.db = await aiosqlite.connect(self.db_path)

        # 创建知识表
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        # 创建索引
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_category
            ON knowledge(category)
        """)

        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_tags
            ON knowledge(tags)
        """)

        # 创建对话摘要表
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS conversation_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                summary TEXT NOT NULL,
                key_points TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await self.db.commit()
        logger.info(f"长期记忆初始化完成: {self.db_path}")

    async def store(
        self,
        key: str,
        value: Any,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ):
        """
        存储知识

        Args:
            key: 键
            value: 值
            category: 分类
            tags: 标签列表
            metadata: 元数据
        """
        if not self.db:
            await self.initialize()

        tags_json = json.dumps(tags, ensure_ascii=False) if tags else None
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None
        value_json = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value

        await self.db.execute(
            """
            INSERT OR REPLACE INTO knowledge (key, value, category, tags, updated_at, metadata)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            """,
            (key, value_json, category, tags_json, metadata_json),
        )

        await self.db.commit()

    async def retrieve(self, key: str) -> Optional[Dict]:
        """
        检索知识

        Args:
            key: 键

        Returns:
            知识字典
        """
        if not self.db:
            await self.initialize()

        cursor = await self.db.execute(
            """
            SELECT key, value, category, tags, created_at, updated_at, metadata
            FROM knowledge
            WHERE key = ?
            """,
            (key,),
        )

        row = await cursor.fetchone()

        if row:
            return self._row_to_dict(row)

        return None

    async def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        搜索知识

        Args:
            query: 搜索关键词
            category: 分类
            tags: 标签列表
            limit: 限制数量

        Returns:
            知识列表
        """
        if not self.db:
            await self.initialize()

        conditions = []
        params = []

        if query:
            conditions.append("key LIKE ? OR value LIKE ?")
            params.extend([f"%{query}%", f"%{query}%"])

        if category:
            conditions.append("category = ?")
            params.append(category)

        if tags:
            # 标签搜索（简化版，实际应该用 JSON 查询）
            for tag in tags:
                conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor = await self.db.execute(
            f"""
            SELECT key, value, category, tags, created_at, updated_at, metadata
            FROM knowledge
            WHERE {where_clause}
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            params + [limit],
        )

        rows = await cursor.fetchall()

        return [self._row_to_dict(row) for row in rows]

    async def delete(self, key: str):
        """
        删除知识

        Args:
            key: 键
        """
        if not self.db:
            await self.initialize()

        await self.db.execute("DELETE FROM knowledge WHERE key = ?", (key,))
        await self.db.commit()

    async def list_categories(self) -> List[str]:
        """
        列出所有分类

        Returns:
            分类列表
        """
        if not self.db:
            await self.initialize()

        cursor = await self.db.execute(
            "SELECT DISTINCT category FROM knowledge WHERE category IS NOT NULL"
        )

        rows = await cursor.fetchall()

        return [row[0] for row in rows]

    async def store_conversation_summary(
        self, session_id: str, summary: str, key_points: Optional[List[str]] = None
    ):
        """
        存储对话摘要

        Args:
            session_id: 会话 ID
            summary: 摘要
            key_points: 关键点列表
        """
        if not self.db:
            await self.initialize()

        key_points_json = json.dumps(key_points, ensure_ascii=False) if key_points else None

        await self.db.execute(
            """
            INSERT INTO conversation_summaries (session_id, summary, key_points)
            VALUES (?, ?, ?)
            """,
            (session_id, summary, key_points_json),
        )

        await self.db.commit()

    async def get_conversation_summary(self, session_id: str) -> Optional[Dict]:
        """
        获取对话摘要

        Args:
            session_id: 会话 ID

        Returns:
            摘要字典
        """
        if not self.db:
            await self.initialize()

        cursor = await self.db.execute(
            """
            SELECT session_id, summary, key_points, created_at
            FROM conversation_summaries
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (session_id,),
        )

        row = await cursor.fetchone()

        if row:
            key_points = json.loads(row[2]) if row[2] else None
            return {
                "session_id": row[0],
                "summary": row[1],
                "key_points": key_points,
                "created_at": row[3],
            }

        return None

    def _row_to_dict(self, row) -> Dict:
        """将数据库行转换为字典"""
        tags = json.loads(row[3]) if row[3] else None
        metadata = json.loads(row[6]) if row[6] else None

        # 尝试解析 value 为 JSON
        value = row[1]
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass

        return {
            "key": row[0],
            "value": value,
            "category": row[2],
            "tags": tags,
            "created_at": row[4],
            "updated_at": row[5],
            "metadata": metadata,
        }

    async def close(self):
        """关闭数据库连接"""
        if self.db:
            await self.db.close()
            logger.info("长期记忆数据库已关闭")
