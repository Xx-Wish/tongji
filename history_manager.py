# -*- coding: utf-8 -*-
"""
历史记录管理模块

使用 SQLite 数据库存储每次数据生成的历史记录，
支持记录的增删查改，以及结果数据的序列化和反序列化。
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class HistoryManager:
    """历史记录管理器，基于 SQLite 实现持久化存储"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化历史记录管理器

        Args:
            db_path: 数据库文件路径，默认为程序目录下的 data/history.db
        """
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'history.db')

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at      TEXT    NOT NULL,
                    project_title   TEXT    DEFAULT '',
                    model_type      TEXT    DEFAULT '',
                    files_imported  TEXT    DEFAULT '[]',
                    result_summary  TEXT    DEFAULT '{}',
                    result_data     TEXT    DEFAULT '{}',
                    status          TEXT    DEFAULT 'success',
                    error_message   TEXT    DEFAULT '',
                    duration_sec    REAL    DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_created_at
                ON history(created_at DESC)
            """)
            conn.commit()

    def add_record(
        self,
        project_title: str,
        model_type: str,
        files_imported: List[str],
        result_data: Dict[str, Any],
        status: str = 'success',
        error_message: str = '',
        duration_sec: float = 0
    ) -> int:
        """
        添加一条历史记录

        Args:
            project_title: 项目标题
            model_type: 使用的模型类型
            files_imported: 导入的文件路径列表
            result_data: 生成的结果数据（dict，会被 JSON 序列化）
            status: 状态（success / failed）
            error_message: 错误信息
            duration_sec: 耗时（秒）

        Returns:
            新记录的 ID
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 生成结果摘要
        result_summary = self._make_summary(result_data)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO history (
                    created_at, project_title, model_type,
                    files_imported, result_summary, result_data,
                    status, error_message, duration_sec
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now,
                project_title,
                model_type,
                json.dumps(files_imported, ensure_ascii=False),
                json.dumps(result_summary, ensure_ascii=False),
                json.dumps(result_data, ensure_ascii=False),
                status,
                error_message,
                duration_sec
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_records(self) -> List[Dict[str, Any]]:
        """
        获取所有历史记录（按时间倒序）

        Returns:
            记录列表，每条记录为 dict
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM history
                ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_record_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取单条历史记录

        Args:
            record_id: 记录 ID

        Returns:
            记录 dict，若不存在返回 None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM history WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_record(self, record_id: int) -> bool:
        """
        删除指定 ID 的历史记录

        Args:
            record_id: 要删除的记录 ID

        Returns:
            是否删除成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history WHERE id = ?", (record_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_all(self) -> int:
        """
        清空所有历史记录

        Returns:
            删除的记录条数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM history")
            count = cursor.fetchone()[0]
            cursor.execute("DELETE FROM history")
            conn.commit()
            return count

    def get_stats(self) -> Dict[str, Any]:
        """
        获取历史记录统计信息

        Returns:
            包含总次数、成功次数、失败次数、最近使用模型等信息的 dict
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM history")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM history WHERE status = 'success'")
            success = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM history WHERE status = 'failed'")
            failed = cursor.fetchone()[0]

            cursor.execute("""
                SELECT model_type, COUNT(*) as cnt
                FROM history
                GROUP BY model_type
                ORDER BY cnt DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            most_used_model = row[0] if row else '无'

            cursor.execute("SELECT created_at FROM history ORDER BY created_at DESC LIMIT 1")
            row = cursor.fetchone()
            last_used = row[0] if row else '无'

            return {
                'total': total,
                'success': success,
                'failed': failed,
                'most_used_model': most_used_model,
                'last_used': last_used
            }

    def _make_summary(self, result_data: Dict[str, Any]) -> Dict[str, int]:
        """
        根据结果数据生成摘要（各维度数据条数）

        Args:
            result_data: 完整结果数据

        Returns:
            摘要 dict，键为维度名，值为数据条数
        """
        summary = {}
        if isinstance(result_data, dict):
            for key, value in result_data.items():
                if isinstance(value, list):
                    summary[key] = len(value)
                elif isinstance(value, dict):
                    summary[key] = len(value)
                else:
                    summary[key] = 0
        return summary

    def parse_files(self, files_json: str) -> List[str]:
        """将 JSON 字符串解析为文件名列表（仅保留文件名，去除路径）"""
        try:
            paths = json.loads(files_json)
            return [os.path.basename(p) for p in paths if p]
        except Exception:
            return []

    def parse_result_data(self, result_data_json: str) -> Dict[str, Any]:
        """将结果数据 JSON 解析为 dict"""
        try:
            return json.loads(result_data_json)
        except Exception:
            return {}

    def parse_result_summary(self, result_summary_json: str) -> Dict[str, int]:
        """将结果摘要 JSON 解析为 dict"""
        try:
            return json.loads(result_summary_json)
        except Exception:
            return {}
