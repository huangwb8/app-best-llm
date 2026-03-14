# app-best-llm

基于实时联网搜索的 AI 工具智能推荐应用。

## 项目简介

通过联网调研为用户推荐最合适的 AI 工具组合。核心原则：**禁止依赖预设知识库**，所有推荐基于实时搜索的权威评测数据、社区反馈与官方文档。

## 核心功能

- **需求分析**：通过 2-3 个问题快速理解用户场景（任务类型、技术水平、预算、使用频率）
- **联网调研**：强制执行实时搜索，覆盖 SWE-bench、Chatbot Arena 等权威评测数据
- **多源验证**：关键数据至少 2 个独立来源交叉验证
- **结构化报告**：输出首选方案 + 备选方案，附调研来源链接

## 目录结构

```
app-best-llm/
├── Prompts.md                    # AI 系统提示词（可直接部署）
├── AGENTS.md                     # 项目指令（跨平台通用工作流）
├── CLAUDE.md                     # Claude Code 特定适配
├── CHANGELOG.md                  # 变更记录
├── config.yaml                   # 项目配置（版本号 Single Source of Truth）
├── plans/                        # auto-test-project 优化计划文档
├── tests/                        # auto-test-project 测试会话与报告
└── app-best-llm.code-workspace   # VSCode 工作区配置
```

## AI 辅助开发

本项目配置了 AI 辅助开发支持。启动后 AI 工具会自动读取项目指令文件（CLAUDE.md → AGENTS.md），
按照四步推荐工作流运行：

```bash
# Claude Code（自动读取 CLAUDE.md + AGENTS.md）
claude

# OpenAI Codex CLI（自动读取 AGENTS.md）
codex
```

修改项目指令只需编辑 `AGENTS.md`，`CLAUDE.md` 通过 `@./AGENTS.md` 自动引用。

## 许可证

MIT License
