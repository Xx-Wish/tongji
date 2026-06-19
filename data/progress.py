"""
成员合作进度模块 (Member Progress Tracker)

本模块用于记录和跟踪 tongji 项目中各团队成员的任务完成进度。
每个成员的状态分为: pending(待开始) / in_progress(进行中) / completed(已完成)

使用方法:
    from data.progress import get_all_progress, update_member_progress, print_progress_table

更新日期: 2026-06-19
"""

from datetime import datetime
from typing import Dict, List, Optional

# ============================================================
# 团队成员进度数据
# ============================================================

MEMBERS: List[Dict[str, str]] = [
    {
        "role": "组长",
        "name": "Xx-Wish",
        "github": "https://github.com/Xx-Wish",
        "task": "创建仓库、搭建框架、管理 Issue 与 PR",
        "status": "completed",
        "completed_date": "2026-06-18",
        "notes": "v0.1 初始项目搭建完成，已合并组员A的README PR",
    },
    {
        "role": "组员 A",
        "name": "yxy-code-ux",
        "github": "https://github.com/yxy-code-ux",
        "task": "完善 README 文档与项目介绍",
        "status": "completed",
        "completed_date": "2026-06-18",
        "notes": "PR #7 已合并，README 文档完善完成",
    },
    {
        "role": "组员 B",
        "name": "lighter888",
        "github": "https://github.com/lighter888",
        "task": "制作日志系统",
        "status": "in_progress",
        "completed_date": "",
        "notes": "相关 Issue #2 已创建，等待提交 PR",
    },
    {
        "role": "组员 C",
        "name": "Firefly0688",
        "github": "https://github.com/Firefly0688",
        "task": "制作 API 本地存储功能",
        "status": "in_progress",
        "completed_date": "",
        "notes": "相关 Issue #3 已创建，已提交历史记录功能 PR #8",
    },
    {
        "role": "组员 D",
        "name": "xuanxuanxuan777",
        "github": "https://github.com/xuanxuanxuan777",
        "task": "制作历史记录功能",
        "status": "completed",
        "completed_date": "2026-06-19",
        "notes": "完成 data/progress.py 与 data/changelog.py，完善成员合作信息",
    },
]

STATUS_MAP = {
    "pending": "⏳ 待开始",
    "in_progress": "🔄 进行中",
    "completed": "✅ 已完成",
}


def get_all_progress() -> List[Dict[str, str]]:
    """获取所有成员的进度信息。"""
    return MEMBERS


def get_member_progress(github_username: str) -> Optional[Dict[str, str]]:
    """根据 GitHub 用户名获取单个成员的进度信息。"""
    for member in MEMBERS:
        if member["name"].lower() == github_username.lower():
            return member
    return None


def update_member_progress(
    github_username: str,
    status: Optional[str] = None,
    notes: Optional[str] = None,
) -> bool:
    """更新指定成员的进度状态或备注。

    Args:
        github_username: 成员的 GitHub 用户名
        status: 新状态 (pending / in_progress / completed)
        notes: 新的备注信息

    Returns:
        bool: 更新是否成功
    """
    member = get_member_progress(github_username)
    if member is None:
        return False
    if status is not None and status in STATUS_MAP:
        member["status"] = status
        if status == "completed":
            member["completed_date"] = datetime.now().strftime("%Y-%m-%d")
    if notes is not None:
        member["notes"] = notes
    return True


def get_progress_summary() -> Dict[str, int]:
    """获取团队整体进度概览。"""
    summary = {"total": len(MEMBERS), "completed": 0, "in_progress": 0, "pending": 0}
    for member in MEMBERS:
        status = member["status"]
        if status in summary:
            summary[status] += 1
    return summary


def print_progress_table() -> str:
    """生成格式化的进度表格字符串。"""
    lines = []
    lines.append("=" * 85)
    lines.append(f"{'角色':<8} {'GitHub':<18} {'任务':<28} {'状态':<12} {'完成日期':<12}")
    lines.append("=" * 85)
    for m in MEMBERS:
        status_display = STATUS_MAP.get(m["status"], m["status"])
        lines.append(
            f"{m['role']:<8} {m['name']:<18} {m['task']:<28} {status_display:<12} {m['completed_date']:<12}"
        )
    lines.append("=" * 85)
    summary = get_progress_summary()
    lines.append(
        f"总计 {summary['total']} 人 | 已完成 {summary['completed']} | 进行中 {summary['in_progress']} | 待开始 {summary['pending']}"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(print_progress_table())
