# 开源本地部署视频自动字幕生成工具推荐报告

> **查询日期**：2026-03-14
> **用户场景**：讲课录屏转录 / CLI+GUI 均可 / macOS+Windows / 仅转录（无需翻译）/ 高时间戳精度优先

---

## 首选方案：WhisperX

[GitHub: m-bain/whisperX](https://github.com/m-bain/whisperX)

**推荐理由**

讲课录屏的核心诉求是"高精度时间戳"——标准 Whisper 的时间戳误差可达数秒，WhisperX 通过 wav2vec2 强制对齐将精度压到**词级别（word-level）**，这是其他工具无法替代的核心差异。

**具体数据**

- 速度：large-v3 模型下实时比达 **70x**（即 70 分钟视频约 1 分钟处理完）
- 时间戳精度：词级别对齐，误差在 100ms 以内
- 说话人分离：内置 pyannote，可标注"谁在说话"

**使用方式**

```bash
pip install whisperx
whisperx lecture.mp4 --model large-v3 --output_format srt
```

**隐藏成本**

- 说话人分离功能需要 HuggingFace token（免费注册）
- macOS Apple Silicon 需额外配置（或用 CPU 模式，速度下降约 5x）
- 语言支持开箱限于：`en, fr, de, es, it, ja, zh, nl, uk, pt`

**月费用**：完全免费，模型本地运行

---

## 备选方案 1：whisply

[GitHub: tsmdt/whisply](https://github.com/tsmdt/whisply)

**适用场景**：macOS Apple Silicon 用户，想要开箱即用的跨平台方案

**核心特点**

- 自动选择最优后端：CPU → faster-whisper，Apple M1–M5 → MLX，NVIDIA GPU → insanely-fast-whisper
- 提供 CLI 和简单 GUI 双入口
- 支持批量处理整个目录的视频
- 集成 WhisperX 实现词级时间戳

**局限**：时间戳精度略低于直接使用 WhisperX，对 M 系芯片优化更好

**月费用**：完全免费

---

## 备选方案 2：VideoCaptioner（卡卡字幕助手）

[GitHub: WEIFENG2333/VideoCaptioner](https://github.com/WEIFENG2333/VideoCaptioner)

**适用场景**：不想接触命令行、需要可视化编辑字幕

**核心特点**

- 完整 GUI，一键操作
- 无需 GPU 即可运行
- 内置字幕编辑器，支持实时预览和手动修正
- 性能参考：14 分钟 1080P 视频约 4 分钟处理完

**局限**：时间戳精度为句级别（非词级别），不满足"高精度"需求；需配置 LLM API 才能发挥最佳效果

**月费用**：基础功能免费；若接 LLM API 优化断句，GPT-4o-mini 约 ¥0.01/视频

---

## 更多候选工具

### stable-ts — 无需额外模型的词级时间戳

[GitHub: jianfch/stable-ts](https://github.com/jianfch/stable-ts)

通过修改 Whisper 解码逻辑直接提取词级时间戳，**无需额外的对齐模型**（WhisperX 需要额外下载 wav2vec2）。适合网络受限或磁盘空间有限的场景。

- 最新版：2.19.1（2025-08-16），持续维护
- 支持 `nonspeech_skip` 跳过无声段，减少幻觉
- 输出直接 `.srt`/`.vtt`

```python
import stable_whisper
model = stable_whisper.load_model('large-v3')
result = model.transcribe('lecture.mp4')
result.to_srt_vtt('lecture.srt')
```

**局限**：Whisper 未针对词级时间戳训练，在音乐/背景噪音段可能出现时间轴漂移；WhisperX 的 wav2vec2 对齐更稳定

---

### Buzz — 纯 GUI，零门槛本地转录

[GitHub: chidiwilliams/buzz](https://github.com/chidiwilliams/buzz)

目前功能最完整的 Whisper GUI 前端，macOS/Windows/Linux 三平台原生支持。

- 后端可选：Whisper / Faster-Whisper / Whisper.cpp / HuggingFace 模型
- 支持 Vulkan GPU 加速（2025 新增），~5GB 显存的笔记本 GPU 可跑 large 模型
- 内置高级字幕查看器：搜索、回放控制、变速播放
- 支持转录前人声分离（提升含背景音乐视频的准确率）
- 输出：TXT / SRT / VTT

**适合人群**：完全不想碰命令行，但需要灵活切换模型和后端的用户

---

### insanely-fast-whisper — NVIDIA GPU 极速方案

[GitHub: Vaibhavs10/insanely-fast-whisper](https://github.com/Vaibhavs10/insanely-fast-whisper)

通过 FlashAttention-2 重构注意力层，在高端 NVIDIA GPU 上吞吐量最大化。

- 运行环境：NVIDIA GPU（A100 基准测试）/ Apple MPS
- 支持 distil-whisper（6x 更快，WER 仅差 1%）
- 纯 CLI，适合批量流水线

**局限**：需要较大显存（FlashAttention-2 编译要求高）；无词级时间戳；讲课录屏场景 GPU 利用率不如大批量任务划算

---

### whisper-timestamped — 多语言词级时间戳 + 置信度

[GitHub: linto-ai/whisper-timestamped](https://github.com/linto-ai/whisper-timestamped)

在词级时间戳基础上额外输出**每词置信度分数**，便于后期质检和过滤低质量片段。

- 多语言支持完整（无 WhisperX 的语言限制）
- 输出含置信度的 JSON，可二次处理
- 适合需要程序化过滤低置信词的场景

---

## 横向对比矩阵

| 维度 | WhisperX | stable-ts | Buzz | whisply | VideoCaptioner | insanely-fast-whisper |
|---|---|---|---|---|---|---|
| 时间戳精度 | **词级 wav2vec2** ✅ | 词级（Whisper内部）⚠️ | 句级 ⚠️ | 词级（via WhisperX）✅ | 句级 ⚠️ | 句级 ⚠️ |
| macOS Apple Silicon | 需手动配置 ⚠️ | ✅ | ✅ | **自动 MLX** ✅ | ✅ | MPS 支持 ⚠️ |
| Windows | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| GUI | ❌ CLI | ❌ CLI | **完整 GUI** ✅ | CLI + 简单 GUI | **完整 GUI** ✅ | ❌ CLI |
| 批量处理 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 无需 GPU | ✅（慢） | ✅（慢） | ✅ | ✅ MLX | ✅ | ❌ 推荐 GPU |
| 说话人分离 | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| 额外模型下载 | 需 wav2vec2 ⚠️ | ❌ 无需 ✅ | 无需 ✅ | 按需 | 无需 ✅ | 无需 ✅ |
| 置信度输出 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 月费用 | 免费 | 免费 | 免费 | 免费 | 免费（LLM可选）| 免费 |

---

## 为什么没选

| 工具 | 排除原因 |
|---|---|
| **原版 OpenAI Whisper** | 时间戳误差可达数秒，不满足高精度需求；速度也慢于 WhisperX |
| **video-subtitle-master** | 核心优势是批量翻译，时间戳精度无特别优化，不匹配需求 |
| **auto-subtitle** | 极简工具，无词级时间戳，适合快速处理而非精度要求场景 |
| **subgen** | 专为 Plex/Jellyfin 媒体服务器设计，讲课录屏场景不适用 |
| **insanely-fast-whisper** | 需高端 NVIDIA GPU 才能发挥优势；无词级时间戳；单视频场景不划算 |

---

## 最终选型建议

```
高精度时间戳 + 有网络下载额外模型    →  WhisperX（wav2vec2 对齐，最稳定）
高精度时间戳 + 网络受限/磁盘有限     →  stable-ts（无需额外模型）
macOS Apple Silicon + 想要最快速度   →  whisply（自动 MLX 加速）
完全不想用命令行                     →  Buzz（GUI 最完整，支持多后端）
需要置信度分数做质检                 →  whisper-timestamped
```

---

## 调研来源

- [WhisperX GitHub - 速度/精度数据](https://github.com/m-bain/whisperX)
- [stable-ts GitHub - 词级时间戳实现](https://github.com/jianfch/stable-ts)
- [Buzz GitHub - GUI 功能说明](https://github.com/chidiwilliams/buzz)
- [whisply GitHub - 多后端自动选择](https://github.com/tsmdt/whisply)
- [insanely-fast-whisper GitHub](https://github.com/Vaibhavs10/insanely-fast-whisper)
- [whisper-timestamped GitHub](https://github.com/linto-ai/whisper-timestamped)
- [VideoCaptioner GitHub - 功能说明](https://github.com/WEIFENG2333/VideoCaptioner)
- [Whisper 变体对比 - modal.com](https://modal.com/blog/choosing-whisper-variants)
- [2025 STT Benchmark - ionio.ai](https://www.ionio.ai/blog/2025-edge-speech-to-text-model-benchmark-whisper-vs-competitors)
- [卡卡字幕助手深度测评 - 知乎](https://zhuanlan.zhihu.com/p/28262336823)
