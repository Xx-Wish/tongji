"""
项目更新日志模块 (Project Changelog)

本模块用于记录 tongji 项目各版本的更新历史和成员贡献。
每次更新会记录版本号、日期、贡献者和变更内容。

使用方法:
    from data.changelog import get_changelog, add_changelog_entry, print_changelog

更新日期: 2026-06-19
"""

from datetime import datetime
from typing import Dict, List

# ============================================================
# 更新日志数据
# ============================================================

CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "v0.1",
        "date": "2026-06-18",
        "contributor": "Xx-Wish",
        "role": "组长",
        "content": "创建初始项目，搭建 PyQt5 基础框架，配置仓库结构与 .gitignore",
        "category": "framework",
    },
    {
        "version": "v0.2",
        "date": "2026-06-18",
        "contributor": "yxy-code-ux",
        "role": "组员 A",
        "content": "完善 README 文档，补充项目简介、架构说明、使用教程、FAQ 等内容",
        "category": "documentation",
    },
    {
        "version": "v0.3",
        "date": "2026-06-19",
        "contributor": "xuanxuanxuan777",
        "role": "组员 D",
        "content": "创建 data/progress.py（成员进度追踪）与 data/changelog.py（更新日志），完善成员合作信息",
        "category": "collaboration",
    },
]

CATEGORY_MAP = {
    "framework": "🏗️ 框架搭建",
    "documentation": "📖 文档完善",
    "feature": "✨ 新功能",
    "bugfix": "🐛 问题修复",
    "collaboration": "👥 协作信息",
    "other": "📦 其他",
}


def get_changelog() -> List[Dict[str, str]]:
    """获取完整的更新日志列表。"""
    return CHANGELOG


def get_changelog_by_version(version: str) -> List[Dict[str, str]]:
    """根据版本号筛选更新日志。"""
    return [entry for entry in CHANGELOG if entry["version"] == version]


def get_changelog_by_contributor(github_username: str) -> List[Dict[str, str]]:
    """根据贡献者 GitHub 用户名筛选更新日志。"""
    return [
        entry
        for entry in CHANGELOG
        if entry["contributor"].lower() == github_username.lower()
    ]


def add_changelog_entry(
    version: str,
    contributor: str,
    role: str,
    content: str,
    category: str = "other",
    date: str = "",
) -> None:
    """添加一条新的更新日志记录。

    Args:
        version: 版本号（如 "v0.4"）
        contributor: 贡献者 GitHub 用户名
        role: 贡献者角色（如 "组员 D"）
        content: 变更内容描述
        category: 变更类别（framework/documentation/feature/bugfix/collaboration/other）
        date: 日期，留空则使用今天日期
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    entry = {
        "version": version,
        "date": date,
        "contributor": contributor,
        "role": role,
        "content": content,
        "category": category,
    }
    CHANGELOG.append(entry)


def get_contributor_summary() -> Dict[str, int]:
    """获取贡献者统计（每人贡献次数）。"""
    summary: Dict[str, int] = {}
    for entry in CHANGELOG:
        contributor = entry["contributor"]
        summary[contributor] = summary.get(contributor, 0) + 1
    return summary


def print_changelog() -> str:
    """生成格式化的更新日志表格字符串。"""
    lines = []
    lines.append("=" * 90)
    lines.append(f"{'版本':<6} {'日期':<12} {'贡献者':<18} {'角色':<8} {'类别':<12} {'内容'}")
    lines.append("=" * 90)
    for entry in CHANGELOG:
        cat_display = CATEGORY_MAP.get(entry["category"], entry["category"])
        lines.append(
            f"{entry['version']:<6} {entry['date']:<12} {entry['contributor']:<18} "
            f"{entry['role']:<8} {cat_display:<12} {entry['content']}"
        )
    lines.append("=" * 90)
    summary = get_contributor_summary()
    summary_str = " | ".join(f"{k}: {v}次" for k, v in summary.items())
    lines.append(f"贡献统计: {summary_str}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(print_changelog())
