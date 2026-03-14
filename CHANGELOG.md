# Changelog

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [1.2.1] - 2026-03-14

### Changed（变更）

- `CLAUDE.md`（B-P1-1）：更新 AGENTS.md 定位描述，从"跨平台通用"改为"项目主指令文件（含平台适配说明）"
- `CLAUDE.md`（B-P1-3）：移除末尾重复的变更记录提示，避免与 AGENTS.md 变更管理章节重复（DRY 修复）
- `CLAUDE.md`（B-P2-1）：删除过时外部 URL（agents.md 标准链接、GitHub issue 链接）
- `AGENTS.md`（B-P1-5）：将"方案输出"章节从引用 Prompts.md 改为自包含列表，解除与 Prompts.md 的循环依赖
- `AGENTS.md`（B-P2-4）：KISS 工程原则示例从"最多 3 个工具"改为"需求画像 3-5 问"，消除与 Prompts.md 约束条件的重复表述
- `README.md`（B-P2-3）：AI 辅助开发章节补充说明，描述 AI 工具如何自动读取项目指令文件

## [1.2.0] - 2026-03-14

### Added（新增）

- `AGENTS.md` 新增"深度维度"需求收集：当前痛点 / 已有工具栈 / 决策优先级（三项不可省略）
- `AGENTS.md` 新增竞品差异对比维度：要求搜索 `[工具A] vs [工具B]`，记录独特优势与已知短板
- `AGENTS.md` 新增隐藏成本挖掘维度：API 配额、超额费用、数据隐私政策、迁移成本
- `AGENTS.md` 新增生态健康度维度：维护活跃度、社区规模、企业背书
- `AGENTS.md` 新增输出前质量门控自检清单（5 项）
- `Prompts.md` 新增横向对比矩阵输出模板（10 维度对比表格）
- `Prompts.md` 新增"为什么没选"章节模板：针对用户场景说明排除理由
- `Prompts.md` 新增工具组合建议章节：主工具 + 推荐搭配 + 不推荐叠加
- `Prompts.md` 新增避坑指南章节：常见陷阱 + 隐藏成本提示
- `Prompts.md` 新增快速上手路线章节：面向用户技术水平的 3 步入门路径
- `Prompts.md` 新增"选择备选而非首选的场景"说明，明确各方案的适用边界
- `config.yaml` 新增工作流参数：`require_deep_profile`、`require_benchmark_values`
- `config.yaml` 新增输出规范参数：`require_comparison_matrix`、`require_why_not_section`、`require_tool_combination`、`require_pitfall_guide`

### Changed（变更）

- `AGENTS.md` 三步工作流升级为四步（新增"候选工具发现"作为独立阶段）
- `AGENTS.md` 新增"具体化原则"约束：禁止"性能强大" / "功能丰富"类空洞描述
- `Prompts.md` Identity 升级：明确"有观点、有数据支撑、直击痛点"的角色定位
- `Prompts.md` 首选方案模板升级：推荐理由必须引用具体数据并直接关联用户痛点

## [1.1.0] - 2026-03-14

### Added（新增）

- 新增 `config.yaml`：作为版本号管理的 Single Source of Truth，包含工作流参数与输出规范（修复 P0-1）
- 新增 `plans/` 目录：存放 auto-test-project 优化计划文档
- 新增 `tests/` 目录：存放 auto-test-project 测试会话与报告
- 新增异常处理规范至工作流（P1-4）：处理搜索无结果、无 benchmark、价格不可用等场景
- 新增评测来源质量标准（P2-4）：明确优先权威 benchmark，排除未验证来源

### Changed（变更）

- 重构 `AGENTS.md`（P0-2 + P1-1 + P1-6）：从 236 行精简至 ~70 行；明确平台适配定位；移出维护类内容；工程原则精简为 3 条有本项目体现的条目
- 精简 `CHANGELOG.md`（P1-2）：移除嵌入的使用手册（原 26-109 行），只保留实际变更记录
- 更新 `Prompts.md`（P1-3 + P1-5 + P2-2）：清理临时对话上下文，添加标准输出模板，与 AGENTS.md 工作流职责分离
- 更新 `README.md`（P2-1）：目录树同步反映 plans/ 和 tests/ 的实际结构

## [1.0.0] - 2026-03-14

### Added（新增）

- 初始化项目：AI 工具智能推荐应用（基于实时联网搜索）
- 生成 `AGENTS.md`：配置项目目标、三步核心工作流（需求分析 → 联网调研 → 方案输出）
- 生成 `CLAUDE.md`：通过 `@./AGENTS.md` 自动引用 + Claude Code 特定适配
- 生成 `README.md`：项目介绍与目录结构说明
- 生成 `.gitignore`：包含安全优先的忽略规则
- 写入 `Prompts.md`：AI 工具评测专家系统提示词
