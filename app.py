"""AI 工具智能推荐程序 - Streamlit 主应用"""
import sys
from pathlib import Path

import streamlit as st

# 确保 src 可导入
sys.path.insert(0, str(Path(__file__).parent))

from src.recommender import Recommender, CATEGORY_KEYWORDS, BUDGET_LEVELS, TECH_LEVELS
from src.exporter import generate_markdown, generate_pdf, CATEGORY_NAMES, BUDGET_NAMES, TECH_NAMES

# ── 页面配置 ──────────────────────────────────────────────────
st.set_page_config(
    page_title="AI 工具推荐助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 会话状态初始化 ────────────────────────────────────────────
def _init_state():
    defaults = {
        "step": 0,           # 对话步骤
        "messages": [],      # 聊天记录
        "user_task": "",     # 用户任务描述
        "categories": [],    # 识别的场景类别
        "budget": "medium",  # 预算偏好
        "tech_level": "beginner",  # 技术水平
        "results": [],       # 推荐结果
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

recommender = Recommender()

# ── 工具函数 ──────────────────────────────────────────────────
def add_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})

def reset():
    for k in ["step", "messages", "user_task", "categories", "budget", "tech_level", "results"]:
        del st.session_state[k]
    _init_state()
    st.rerun()

# ── 对话步骤处理 ──────────────────────────────────────────────
WELCOME_MSG = """你好！我是 **AI 工具推荐助手** 🤖

我会根据你的具体需求，从 20+ 款主流 AI 工具中为你推荐最合适的组合。

**请描述你想用 AI 完成什么任务？**

例如：
- "我想用 AI 帮我写代码，主要是 Python 脚本"
- "需要生成产品宣传图片"
- "想把会议录音转成文字"
- "需要分析一份 Excel 数据"
"""

BUDGET_MSG = """明白了！接下来问一下你的**预算偏好**：

请选择下方选项，或直接输入你的想法。"""

TECH_MSG = """好的！最后一个问题——你的**技术水平**如何？

这会影响我推荐工具的复杂度。"""

def handle_step_0():
    """欢迎步骤：展示欢迎消息"""
    if not st.session_state.messages:
        add_message("assistant", WELCOME_MSG)

def handle_task_input(user_input: str):
    """处理用户任务描述"""
    st.session_state.user_task = user_input
    categories = recommender.classify_scenario(user_input)
    st.session_state.categories = categories
    cat_names = "、".join(CATEGORY_NAMES.get(c, c) for c in categories[:2])
    add_message("assistant", f"识别到你的需求属于 **{cat_names}** 场景。\n\n{BUDGET_MSG}")
    st.session_state.step = 2

def handle_budget_input(budget: str):
    """处理预算选择"""
    st.session_state.budget = budget
    add_message("assistant", f"预算：**{BUDGET_NAMES[budget]}** ✅\n\n{TECH_MSG}")
    st.session_state.step = 3

def handle_tech_input(tech: str):
    """处理技术水平选择"""
    st.session_state.tech_level = tech
    add_message("assistant", f"技术水平：**{TECH_NAMES[tech]}** ✅\n\n正在为你分析最佳工具组合...")
    st.session_state.step = 4
    # 执行推荐
    results = recommender.recommend(
        categories=st.session_state.categories,
        budget=st.session_state.budget,
        tech_level=st.session_state.tech_level,
        top_n=3,
    )
    st.session_state.results = results


# ── 推荐结果渲染 ──────────────────────────────────────────────
def render_score_bar(score: float, max_score: float = 10.0) -> str:
    filled = round(score / max_score * 8)
    return "█" * filled + "░" * (8 - filled)


def render_results():
    results = st.session_state.results
    if not results:
        st.warning("未找到符合条件的工具，请尝试调整预算或技术水平。")
        return

    cat_names = "、".join(CATEGORY_NAMES.get(c, c) for c in st.session_state.categories[:2])
    st.success(f"为你找到 **{len(results)}** 款最适合「{cat_names}」场景的工具")

    # Top 3 卡片
    cols = st.columns(len(results))
    for i, (col, result) in enumerate(zip(cols, results)):
        tool = result.tool
        s = tool.get("scores", {})
        with col:
            medal = ["🥇", "🥈", "🥉"][i]
            st.markdown(f"### {medal} {tool['name']}")
            st.caption(tool.get("description", ""))
            st.metric("综合评分", f"{s.get('overall', 0):.1f} / 10")
            st.progress(s.get("overall", 0) / 10)

            with st.expander("详细评分"):
                for dim, label in [
                    ("ease_of_use", "易用性"),
                    ("quality", "质量"),
                    ("value", "性价比"),
                ]:
                    v = s.get(dim, 0)
                    st.write(f"**{label}** {v:.1f}/10  {render_score_bar(v)}")

            with st.expander("价格方案"):
                pricing = tool.get("pricing", {})
                if pricing.get("free_tier"):
                    st.success(f"✅ {pricing.get('free_description', '有免费版')}")
                for plan in pricing.get("paid_plans", []):
                    st.write(f"- **{plan['name']}**：${plan['price']}/{plan['unit']}")

            with st.expander("优势 / 局限"):
                for pro in tool.get("pros", []):
                    st.write(f"✅ {pro}")
                for con in tool.get("cons", []):
                    st.write(f"⚠️ {con}")

    # 横向对比表
    st.markdown("---")
    st.markdown("#### 横向对比")
    table_data = []
    for result in results:
        tool = result.tool
        s = tool.get("scores", {})
        pricing = tool.get("pricing", {})
        has_free = "✅" if pricing.get("free_tier") else "❌"
        min_price = result.min_paid_price
        price_str = f"${min_price:.0f}/月" if min_price > 0 else "免费"
        table_data.append({
            "工具": tool["name"],
            "综合": f"{s.get('overall', 0):.1f}",
            "易用性": f"{s.get('ease_of_use', 0):.1f}",
            "质量": f"{s.get('quality', 0):.1f}",
            "性价比": f"{s.get('value', 0):.1f}",
            "免费版": has_free,
            "最低月费": price_str,
        })
    st.table(table_data)

    # 成本估算
    st.markdown("#### 月度成本估算")
    budget_label = BUDGET_NAMES.get(st.session_state.budget, "")
    st.info(f"预算偏好：{budget_label}")
    for result in results:
        tool = result.tool
        pricing = tool.get("pricing", {})
        if pricing.get("free_tier"):
            st.write(f"- **{tool['name']}**：可从免费版开始，{pricing.get('free_description', '')}")
        else:
            plans = pricing.get("paid_plans", [])
            if plans:
                cheapest = min(plans, key=lambda p: p.get("price", 999))
                st.write(f"- **{tool['name']}**：最低 ${cheapest['price']}/{cheapest['unit']}（{cheapest['name']}）")

    # 导出按钮
    st.markdown("---")
    st.markdown("#### 导出报告")
    md_content = generate_markdown(
        results=results,
        user_task=st.session_state.user_task,
        categories=st.session_state.categories,
        budget=st.session_state.budget,
        tech_level=st.session_state.tech_level,
    )
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 下载 Markdown 报告",
            data=md_content.encode("utf-8"),
            file_name="ai_tools_recommendation.md",
            mime="text/markdown",
        )
    with col2:
        try:
            pdf_bytes = generate_pdf(md_content)
            st.download_button(
                label="📑 下载 PDF 报告",
                data=pdf_bytes,
                file_name="ai_tools_recommendation.pdf",
                mime="application/pdf",
            )
        except ImportError:
            st.caption("PDF 导出需安装 fpdf2：`pip install fpdf2`")


# ── 主界面 ────────────────────────────────────────────────────
st.title("🤖 AI 工具推荐助手")
st.caption("根据你的需求，从 20+ 款主流 AI 工具中找到最合适的组合")

# 初始化欢迎消息
handle_step_0()

# 渲染聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 步骤 2：预算选择（按钮）
if st.session_state.step == 2:
    cols = st.columns(4)
    budget_options = [
        ("free", "🆓 仅免费"),
        ("low", "💰 低预算\n≤$20/月"),
        ("medium", "💳 中等\n≤$50/月"),
        ("high", "💎 不限预算"),
    ]
    for col, (key, label) in zip(cols, budget_options):
        if col.button(label, key=f"budget_{key}", use_container_width=True):
            add_message("user", BUDGET_NAMES[key])
            handle_budget_input(key)
            st.rerun()

# 步骤 3：技术水平选择（按钮）
elif st.session_state.step == 3:
    cols = st.columns(3)
    tech_options = [
        ("beginner", "🌱 初学者\n不懂编程"),
        ("intermediate", "🔧 中级用户\n会一点代码"),
        ("advanced", "⚡ 高级用户\n开发者/工程师"),
    ]
    for col, (key, label) in zip(cols, tech_options):
        if col.button(label, key=f"tech_{key}", use_container_width=True):
            add_message("user", TECH_NAMES[key])
            handle_tech_input(key)
            st.rerun()

# 步骤 4：展示推荐结果
elif st.session_state.step == 4:
    render_results()

# 步骤 1：用户输入任务（chat input）
if st.session_state.step in (0, 1):
    if user_input := st.chat_input("描述你的任务需求..."):
        add_message("user", user_input)
        handle_task_input(user_input)
        st.rerun()

# 重置按钮
if st.session_state.step > 0:
    st.markdown("---")
    if st.button("🔄 重新开始", use_container_width=False):
        reset()
