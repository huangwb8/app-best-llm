"""报告导出：生成 Markdown 和 PDF 格式的推荐报告"""
from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from src.recommender import ToolResult

CATEGORY_NAMES = {
    "coding": "编程开发",
    "writing": "写作助手",
    "image": "图像生成",
    "audio": "语音处理",
    "research": "搜索与调研",
    "data": "数据分析",
    "video": "视频生成",
    "foundation": "基础模型",
}

BUDGET_NAMES = {
    "free": "仅免费工具",
    "low": "低预算（≤$20/月）",
    "medium": "中等预算（≤$50/月）",
    "high": "不限预算",
}

TECH_NAMES = {
    "beginner": "初学者",
    "intermediate": "中级用户",
    "advanced": "高级用户/开发者",
}


def _score_bar(score: float, max_score: float = 10.0, width: int = 10) -> str:
    filled = round(score / max_score * width)
    return "█" * filled + "░" * (width - filled)


def _format_pricing(tool: dict) -> str:
    pricing = tool.get("pricing", {})
    lines = []
    if pricing.get("free_tier"):
        lines.append(f"- 免费版：{pricing.get('free_description', '有免费版')}")
    for plan in pricing.get("paid_plans", []):
        lines.append(f"- {plan['name']}：${plan['price']}/{plan['unit']}")
    return "\n".join(lines) if lines else "- 价格信息暂无"


def generate_markdown(
    results: list[ToolResult],
    user_task: str,
    categories: list[str],
    budget: str,
    tech_level: str,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cat_names = "、".join(CATEGORY_NAMES.get(c, c) for c in categories)

    lines = [
        f"# AI 工具推荐报告",
        f"",
        f"> 生成时间：{now}",
        f"",
        f"## 需求摘要",
        f"",
        f"| 项目 | 内容 |",
        f"|------|------|",
        f"| 任务描述 | {user_task} |",
        f"| 识别场景 | {cat_names} |",
        f"| 预算偏好 | {BUDGET_NAMES.get(budget, budget)} |",
        f"| 技术水平 | {TECH_NAMES.get(tech_level, tech_level)} |",
        f"",
        f"## Top {len(results)} 推荐工具",
        f"",
    ]

    for i, result in enumerate(results, 1):
        tool = result.tool
        scores = tool.get("scores", {})
        lines += [
            f"### {i}. {tool['name']}",
            f"",
            f"**{tool.get('description', '')}**",
            f"",
            f"#### 评分",
            f"",
            f"| 维度 | 评分 | 可视化 |",
            f"|------|------|--------|",
            f"| 综合 | {scores.get('overall', 0):.1f}/10 | {_score_bar(scores.get('overall', 0))} |",
            f"| 易用性 | {scores.get('ease_of_use', 0):.1f}/10 | {_score_bar(scores.get('ease_of_use', 0))} |",
            f"| 质量 | {scores.get('quality', 0):.1f}/10 | {_score_bar(scores.get('quality', 0))} |",
            f"| 性价比 | {scores.get('value', 0):.1f}/10 | {_score_bar(scores.get('value', 0))} |",
            f"",
            f"#### 价格方案",
            f"",
            _format_pricing(tool),
            f"",
            f"#### 优势",
            f"",
        ]
        for pro in tool.get("pros", []):
            lines.append(f"- ✅ {pro}")
        lines += [f"", f"#### 局限", f""]
        for con in tool.get("cons", []):
            lines.append(f"- ⚠️ {con}")
        lines += [f"", f"#### 适用场景", f""]
        for uc in tool.get("use_cases", []):
            lines.append(f"- {uc}")
        lines.append(f"")

    # 横向对比表
    lines += [
        f"## 横向对比",
        f"",
        f"| 工具 | 综合 | 易用性 | 质量 | 性价比 | 免费版 | 最低月费 |",
        f"|------|------|--------|------|--------|--------|----------|",
    ]
    for result in results:
        tool = result.tool
        s = tool.get("scores", {})
        has_free = "✅" if tool.get("pricing", {}).get("free_tier") else "❌"
        min_price = result.min_paid_price
        price_str = f"${min_price:.0f}" if min_price > 0 else "免费"
        lines.append(
            f"| {tool['name']} | {s.get('overall',0):.1f} | {s.get('ease_of_use',0):.1f} "
            f"| {s.get('quality',0):.1f} | {s.get('value',0):.1f} | {has_free} | {price_str} |"
        )

    lines += [
        f"",
        f"---",
        f"",
        f"*本报告由 AI 工具推荐助手生成，数据来源：SWE-bench、Chatbot Arena、社区反馈*",
    ]
    return "\n".join(lines)


def generate_pdf(markdown_content: str) -> bytes:
    """将 Markdown 内容转换为 PDF 字节流（使用 fpdf2）"""
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("请安装 fpdf2：pip install fpdf2")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 尝试加载中文字体（如果有），否则使用内置字体
    try:
        import os
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        ]
        font_loaded = False
        for fp in font_paths:
            if os.path.exists(fp):
                pdf.add_font("CJK", "", fp, uni=True)
                pdf.add_font("CJK", "B", fp, uni=True)
                font_loaded = True
                break
        if not font_loaded:
            raise FileNotFoundError
        cjk_font = "CJK"
    except Exception:
        cjk_font = "Helvetica"

    for line in markdown_content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# "):
            pdf.set_font(cjk_font, "B", 16)
            pdf.cell(0, 10, stripped[2:], ln=True)
        elif stripped.startswith("## "):
            pdf.set_font(cjk_font, "B", 13)
            pdf.cell(0, 8, stripped[3:], ln=True)
        elif stripped.startswith("### "):
            pdf.set_font(cjk_font, "B", 11)
            pdf.cell(0, 7, stripped[4:], ln=True)
        elif stripped.startswith("|"):
            pdf.set_font(cjk_font, "", 8)
            pdf.cell(0, 5, stripped, ln=True)
        elif stripped.startswith("- "):
            pdf.set_font(cjk_font, "", 9)
            pdf.cell(0, 5, "  " + stripped, ln=True)
        elif stripped.startswith(">"):
            pdf.set_font(cjk_font, "", 9)
            pdf.cell(0, 5, stripped[1:].strip(), ln=True)
        elif stripped == "---":
            pdf.ln(3)
        elif stripped:
            pdf.set_font(cjk_font, "", 10)
            pdf.multi_cell(0, 5, stripped)
        else:
            pdf.ln(2)

    return bytes(pdf.output())
