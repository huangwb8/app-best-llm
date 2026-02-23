# AI 工具智能推荐程序

基于 Python + Streamlit 的 AI 工具智能推荐系统，帮助用户根据具体需求快速找到最合适的 AI 工具组合。

## 特性

- **多轮对话式推荐**：问答引导用户描述任务场景、预算、技术水平
- **智能场景分类**：自动识别任务类型（代码/写作/学术/创意/多媒体/数据分析）
- **Top 3 工具推荐**：每个场景推荐最优工具，附评分和横向对比
- **成本估算**：提供免费/付费方案对比，估算月度使用成本
- **报告导出**：支持导出 Markdown/PDF 格式推荐报告

## 工具覆盖范围

| 类别 | 工具 |
|------|------|
| 编程开发 | Claude Code、Cursor、Windsurf、GitHub Copilot |
| 基础模型 | Claude、GPT-4o/o3、Gemini、DeepSeek、Llama |
| 写作助手 | Notion AI、Jasper、Claude.ai、ChatGPT |
| 图像生成 | Midjourney、DALL-E 3、Flux、Ideogram |
| 语音处理 | Whisper、ElevenLabs、Suno |
| 搜索与调研 | Perplexity、Exa、Tavily |
| 数据分析 | Julius AI、Code Interpreter |
| 视频生成 | Sora、Runway、Kling |

## 快速开始

### 环境要求

- Python 3.10+
- pip 或 uv

### 安装

```bash
pip install -r requirements.txt
```

### 运行

```bash
streamlit run app.py
```

## 目录结构

```
app-best-llm/
├── app.py                  # Streamlit 主入口
├── data/
│   └── tools.yaml          # AI 工具数据库（评分、价格、适用场景）
├── core/
│   ├── recommender.py      # 推荐引擎
│   ├── classifier.py       # 场景分类器
│   └── cost_estimator.py   # 成本估算器
├── utils/
│   └── exporter.py         # Markdown/PDF 导出
├── requirements.txt
└── README.md
```

## 数据来源

- 编程工具：SWE-bench、LiveCodeBench、Aider Leaderboard
- 基础模型：Chatbot Arena (LMSYS)、MMLU、HumanEval
- 社区反馈：Reddit、Hacker News、知乎

## AI 辅助开发

本项目配置了 AI 辅助开发支持：

```bash
# Claude Code
claude

# OpenAI Codex CLI
codex
```

**变更记录**：凡是项目的更新，都要统一在 `CHANGELOG.md` 文件里记录。

## 许可证

MIT License
