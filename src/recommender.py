"""推荐引擎：根据用户需求从工具数据库中筛选并排序 Top N 工具"""
from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# 场景关键词映射
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "coding": ["代码", "编程", "开发", "debug", "调试", "重构", "API", "程序", "软件", "脚本"],
    "writing": ["写作", "文章", "博客", "文案", "内容", "翻译", "邮件", "报告", "文档", "论文"],
    "image": ["图片", "图像", "绘图", "设计", "插画", "海报", "视觉", "美术", "生图"],
    "audio": ["语音", "音频", "音乐", "配音", "转录", "字幕", "播客", "歌曲"],
    "research": ["搜索", "调研", "查找", "信息", "资料", "学术", "分析", "新闻"],
    "data": ["数据", "分析", "统计", "图表", "可视化", "Excel", "CSV", "数据库"],
    "video": ["视频", "短片", "动画", "影片", "剪辑", "特效"],
    "foundation": ["对话", "聊天", "问答", "推理", "通用", "助手"],
}

BUDGET_LEVELS = {
    "free": 0,
    "low": 20,      # ≤ $20/月
    "medium": 50,   # ≤ $50/月
    "high": 999,    # 不限
}

TECH_LEVELS = {"beginner": 1, "intermediate": 2, "advanced": 3}


@dataclass
class ToolResult:
    tool: dict[str, Any]
    score: float
    match_reasons: list[str] = field(default_factory=list)

    @property
    def min_paid_price(self) -> float:
        plans = self.tool.get("pricing", {}).get("paid_plans", [])
        if not plans:
            return 0.0
        return min(p.get("price", 0) for p in plans)

    @property
    def has_free_tier(self) -> bool:
        return self.tool.get("pricing", {}).get("free_tier", False)


class Recommender:
    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "tools.yaml"
        with open(db_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.tools: list[dict] = data.get("tools", [])

    def classify_scenario(self, text: str) -> list[str]:
        """从用户描述中识别场景类别，返回匹配的类别列表（按相关度排序）"""
        text_lower = text.lower()
        scores: dict[str, int] = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw.lower() in text_lower)
            if count > 0:
                scores[category] = count
        if not scores:
            return ["foundation"]  # 默认通用场景
        return sorted(scores, key=lambda c: scores[c], reverse=True)

    def recommend(
        self,
        categories: list[str],
        budget: str = "medium",
        tech_level: str = "beginner",
        top_n: int = 3,
    ) -> list[ToolResult]:
        """返回 Top N 推荐工具"""
        budget_limit = BUDGET_LEVELS.get(budget, 50)
        user_tech = TECH_LEVELS.get(tech_level, 1)

        results: list[ToolResult] = []
        for tool in self.tools:
            if tool.get("category") not in categories:
                continue

            reasons: list[str] = []
            score = tool["scores"]["overall"]

            # 预算过滤：免费版或最低付费价格在预算内
            min_price = min(
                (p.get("price", 0) for p in tool.get("pricing", {}).get("paid_plans", [])),
                default=0,
            )
            has_free = tool.get("pricing", {}).get("free_tier", False)
            if budget == "free" and not has_free:
                continue
            if not has_free and min_price > budget_limit:
                score *= 0.7  # 超预算降权
            elif has_free:
                reasons.append("有免费版")
                score += 0.3

            # 技术水平匹配
            tool_tech = TECH_LEVELS.get(tool.get("technical_level", "beginner"), 1)
            if tool_tech <= user_tech:
                reasons.append("适合你的技术水平")
                score += 0.2
            elif tool_tech > user_tech + 1:
                score -= 0.5  # 技术门槛过高降权

            # 性价比加权
            score += tool["scores"]["value"] * 0.1

            results.append(ToolResult(tool=tool, score=score, match_reasons=reasons))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_n]

    def get_all_categories(self) -> list[str]:
        return sorted({t["category"] for t in self.tools})

    def get_tool_by_id(self, tool_id: str) -> dict | None:
        return next((t for t in self.tools if t["id"] == tool_id), None)
