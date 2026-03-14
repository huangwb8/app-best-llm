# 开源文字转视频 AI 本地部署方案

> 调研日期：2026-03-14
> 需求：开源、可本地部署的文字转视频（Text-to-Video）AI 方案

---

## 核心推荐方案

### 1. Wan2.1 / Wan2.2（阿里巴巴）— 首选

- **许可证**：Apache 2.0（可商用）
- **最低显存**：8GB（1.3B 版本）
- **亮点**：VBench 榜单第一（86.22%）；支持中英文双语提示词；T2V / I2V / 首尾帧生成全覆盖；RTX 3060 即可跑
- **部署方式**：ComfyUI 一键包，最易上手
- **GitHub**：[Wan-Video/Wan2.1](https://github.com/Wan-Video/Wan2.1)

### 2. HunyuanVideo v1.5（腾讯）

- **许可证**：开源（注意：部分 Tencent 模型有地区限制，使用前需确认）
- **最低显存**：14GB（v1.5 开启 offloading 后）
- **亮点**：130 亿参数；双流 Transformer 架构，指令遵循强；支持 T2V、I2V、动态文字特效
- **GitHub**：[Tencent/HunyuanVideo](https://github.com/Tencent/HunyuanVideo)

### 3. LTX-Video / LTX-2（Lightricks）

- **许可证**：开源
- **最低显存**：12GB（LTX-Video）
- **亮点**：LTX-2 是首个单次推理同时生成**音频 + 视频**的开源模型；支持 4K @ 50fps；ComfyUI 直接集成
- **项目地址**：[ltx.io/model](https://ltx.io/model)

### 4. CogVideoX 1.5（智谱 AI）

- **许可证**：Apache 2.0（可商用）
- **最低显存**：12GB（2B 版本）/ 16GB（5B 版本）
- **亮点**：5B 参数；单张 RTX 4090 可微调；支持 10 秒视频 + 任意分辨率 I2V；科研/教育首选
- **GitHub**：[THUDM/CogVideo](https://github.com/zai-org/CogVideo)

### 5. Open-Sora 2.0（ColossalAI）

- **许可证**：开源（含完整训练代码）
- **最低显存**：40GB+（生产级）
- **亮点**：11B 参数；VBench 与 HunyuanVideo 持平；训练成本仅 $20 万；完全开源包括训练代码
- **GitHub**：[hpcaitech/Open-Sora](https://github.com/hpcaitech/Open-Sora)

### 6. SkyReels V2（昆仑万维）

- **许可证**：开源
- **最低显存**：14GB（V2 轻量版）
- **亮点**：基于 HunyuanVideo 微调 1000 万影视片段；专注真实人物生成；33 种面部表情 + 400+ 动作组合；开源 T2V VBench SOTA（82.43）
- **GitHub**：[SkyworkAI/SkyReels-V1](https://github.com/SkyworkAI/SkyReels-V1)

---

## 选型对比表

| 模型 | 最低显存 | 许可证 | 部署难度 | 特色 |
|------|---------|--------|---------|------|
| **Wan2.1** | 8GB | Apache 2.0 | 低 | 综合最强，中文支持 |
| **HunyuanVideo** | 14GB | 开源 | 中 | 指令遵循优秀 |
| **LTX-2** | 12GB | 开源 | 低 | 音视频同步生成，4K |
| **CogVideoX 1.5** | 12GB | Apache 2.0 | 低 | 可微调，科研友好 |
| **Open-Sora 2.0** | 40GB+ | 开源 | 高 | 含训练代码，企业级 |
| **SkyReels V2** | 14GB | 开源 | 中 | 真实人物/影视风格 |

---

## 按显卡配置选型

| 显卡配置 | 推荐方案 |
|---------|---------|
| 消费级（8–12GB） | **Wan2.1-1.3B** + ComfyUI |
| 主流游戏卡（16–24GB） | **HunyuanVideo** 或 **CogVideoX-5B** |
| 专业卡（40GB+） | **Open-Sora 2.0** 或 **SkyReels V1** |
| 需要音视频同步 | **LTX-2** |
| 需要商用且可微调 | **CogVideoX**（Apache 2.0） |

---

## 调研来源

- [Best Open Source AI Video Generation Models in 2026 | Pixazo](https://www.pixazo.ai/blog/best-open-source-ai-video-generation-models)
- [7 Best Open Source Video Generation Models in 2026 | Hyperstack](https://www.hyperstack.cloud/blog/case-study/best-open-source-video-generation-models)
- [Top open-source text-to-video AI models | Modal](https://modal.com/blog/text-to-video-ai-article)
- [Wan2.1 本地部署教程 | 博客园](https://www.cnblogs.com/zhikes/p/18757960)
- [2025年 GitHub 主流开源视频生成模型介绍 | CSDN](https://blog.csdn.net/yanceyxin/article/details/149332495)
- [LTX-2: The Open-Source Audio+Video Generation Model | Medium](https://medium.com/@kapildevkhatik2/ltx-2-the-open-source-audio-video-generation-model-changing-content-creation-979100b131b5)
- [GitHub - hpcaitech/Open-Sora](https://github.com/hpcaitech/Open-Sora)
- [GitHub - THUDM/CogVideo](https://github.com/zai-org/CogVideo)
- [GitHub - SkyworkAI/SkyReels-V1](https://github.com/SkyworkAI/SkyReels-V1)
