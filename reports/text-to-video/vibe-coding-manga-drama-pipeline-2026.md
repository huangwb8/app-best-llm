# AI 漫剧二创 · Vibe Coding 全流程工具链

> **查询日期**：2026-03-14
> **定位**：所有步骤均可通过 Claude Code / 脚本驱动，无需 GUI 操作

---

## 架构总览

```
Claude API          ← 剧本生成 / 分镜解析
    ↓
ComfyUI API         ← 分镜生图 + 角色一致性（本地 REST）
    ↓
Kling API           ← 静帧转动态视频（云端 REST）
    ↓
GPT-SoVITS API      ← 角色配音克隆（本地 REST）
    ↓
FFmpeg CLI          ← 音视频合轨 / 字幕烧录
    ↓
WhisperX CLI        ← 字幕生成（可选，用于转录自己配的音）
```

**原则：所有步骤通过 HTTP 请求或 shell 命令调用，Claude Code 直接编排。**

---

## Step 1 · 剧本生成

**工具**：Claude API（你自己就是这个工具）

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": "根据《凡人修仙传》第XXX章，改编为10分钟短剧剧本，..."
    }]
)
```

**输出格式约定（让 Claude 结构化输出）：**

```json
{
  "scenes": [
    {
      "id": 1,
      "characters": ["韩立", "银月"],
      "background": "洞府内，灵气弥漫",
      "dialogue": [
        {"speaker": "银月", "text": "这龙虾有毒！"},
        {"speaker": "韩立", "text": "..."}
      ],
      "action": "银月指着桌上的龙虾，神情紧张",
      "image_prompt": "xianxia style, indoor cave room, two characters..."
    }
  ]
}
```

---

## Step 2 · 分镜生图（角色一致性）

**工具**：**ComfyUI**（本地部署）+ REST API

### 启动方式

```bash
# 安装
pip install comfyui

# 启动服务（后台运行）
python main.py --listen 0.0.0.0 --port 8188
```

### API 调用模式

ComfyUI 提供 **localhost:8188** REST API，可直接提交 workflow JSON：

```bash
# 提交生图任务
curl -X POST http://127.0.0.1:8188/prompt \
  -H 'Content-Type: application/json' \
  -d '{"prompt": <workflow_json>, "client_id": "vibe-drama"}'
# 返回 {"prompt_id": "abc-123"}

# 轮询结果
curl http://127.0.0.1:8188/history/abc-123
```

### Python 封装

```python
import requests, json, time

def generate_image(workflow: dict, server="127.0.0.1:8188") -> str:
    """提交 ComfyUI workflow，返回图片路径"""
    resp = requests.post(f"http://{server}/prompt",
                         json={"prompt": workflow, "client_id": "vibe"})
    prompt_id = resp.json()["prompt_id"]

    # 等待完成
    while True:
        history = requests.get(f"http://{server}/history/{prompt_id}").json()
        if prompt_id in history:
            outputs = history[prompt_id]["outputs"]
            # 取第一张图的文件名
            for node_id, output in outputs.items():
                if "images" in output:
                    return output["images"][0]["filename"]
        time.sleep(1)
```

### 角色一致性方案

在 ComfyUI workflow JSON 中启用 **IP-Adapter** 节点：

```json
{
  "ip_adapter_node": {
    "class_type": "IPAdapterAdvanced",
    "inputs": {
      "image": ["character_reference_image", 0],
      "weight": 0.8,
      "weight_type": "style transfer precise"
    }
  }
}
```

**Workflow 资源**：[ComfyUI_Workflows GitHub](https://github.com/Jeff-Emmett/ComfyUI_Workflows)（含 Wan 2.2、FLUX 等现成 JSON）

---

## Step 3 · 静帧转动态视频

### 方案 A：Kling API（推荐，质量最优）

**官方 REST API**，支持 image-to-video：

```bash
# 文档：https://app.klingai.com/cn/dev
# 申请 API Key 后即可调用
```

```python
import requests

KLING_API_KEY = "your_key"

def image_to_video(image_path: str, prompt: str, duration: int = 5) -> str:
    """调用可灵 API 生成视频，返回视频下载 URL"""
    with open(image_path, "rb") as f:
        resp = requests.post(
            "https://api.klingai.com/v1/videos/image2video",
            headers={"Authorization": f"Bearer {KLING_API_KEY}"},
            json={
                "image": f.read().hex(),  # 或 base64
                "prompt": prompt,
                "duration": duration,
                "cfg_scale": 0.5
            }
        )
    task_id = resp.json()["data"]["task_id"]
    return poll_kling_task(task_id)
```

**定价参考（2026-03）**：约 ¥0.14/秒视频（5秒片段 ≈ ¥0.7）

### 方案 B：WaveSpeedAI（统一 API，兼容多模型）

```python
# 一套 API，可切换 Kling / Wan / Seedance
# 文档：https://wavespeed.ai
import openai

client = openai.OpenAI(
    base_url="https://api.wavespeed.ai/v1",
    api_key="your_wavespeed_key"
)
```

### 方案 C：Wan2.1（本地开源，免费）

```bash
# 安装
pip install wan

# CLI 生成（图生视频）
wan i2v \
  --image scene_001.png \
  --prompt "xianxia, cave interior, character speaking" \
  --output scene_001.mp4
```

---

## Step 4 · 角色配音克隆

**工具**：**GPT-SoVITS v3**（本地 REST API）

### 启动 API 服务

```bash
# 克隆仓库
git clone https://github.com/RVC-Boss/GPT-SoVITS
cd GPT-SoVITS

# 启动 API server（监听 9880 端口）
python api_v2.py -a 0.0.0.0 -p 9880
```

### 调用示例

```python
import requests

def synthesize_voice(
    text: str,
    ref_audio: str,        # 参考音频路径（角色原声，1-3 分钟）
    ref_text: str,         # 参考音频的文字内容
    output_path: str
):
    """使用 GPT-SoVITS API 合成角色语音"""
    resp = requests.get("http://127.0.0.1:9880/tts", params={
        "text": text,
        "text_lang": "zh",
        "ref_audio_path": ref_audio,
        "prompt_text": ref_text,
        "prompt_lang": "zh",
        "media_type": "wav"
    })
    with open(output_path, "wb") as f:
        f.write(resp.content)
```

### 替代方案：Fish Speech（Docker 部署更简单）

```bash
# Docker 一键启动
docker run -d \
  -p 8080:8080 \
  ghcr.io/evilfreelancer/docker-fish-speech-server:latest

# 调用
curl -X POST http://localhost:8080/v1/tts \
  -H 'Content-Type: application/json' \
  -d '{"text": "银月，这龙虾有毒！", "reference_audio": "yinyue_ref.wav"}'
```

---

## Step 5 · 音视频合成

**工具**：**FFmpeg**（纯 CLI，所有平台通用）

```bash
# 安装
brew install ffmpeg   # macOS
apt install ffmpeg    # Linux

# 合并视频+配音
ffmpeg -i scene_001.mp4 -i scene_001_voice.wav \
  -c:v copy -c:a aac -shortest \
  scene_001_with_audio.mp4

# 批量合并所有场景为完整视频
ffmpeg -f concat -safe 0 -i scenes_list.txt \
  -c copy episode_01_raw.mp4
```

---

## Step 6 · 字幕生成（可选）

**工具**：**WhisperX**（CLI，已在字幕报告中调研）

```bash
pip install whisperx

# 转录最终视频，生成 SRT
whisperx episode_01_raw.mp4 \
  --model large-v3 \
  --language zh \
  --output_format srt \
  --output_dir ./subtitles/

# FFmpeg 烧录字幕
ffmpeg -i episode_01_raw.mp4 \
  -vf subtitles=subtitles/episode_01_raw.srt \
  episode_01_final.mp4
```

---

## 完整 Claude Code 编排脚本骨架

```python
# drama_pipeline.py
# 全流程编排，Claude Code 可以直接 vibe 这个文件

import json
from pathlib import Path
from anthropic import Anthropic
import requests, subprocess

client = Anthropic()

def run_pipeline(source_chapter: str, episode_num: int):
    """完整的一集制作流程"""

    # Step 1: 剧本生成
    script = generate_script(source_chapter)
    scenes = json.loads(script)["scenes"]

    for scene in scenes:
        scene_id = scene["id"]

        # Step 2: 生图
        img_path = generate_image_from_scene(scene)

        # Step 3: 生视频
        video_path = image_to_video(
            img_path,
            prompt=scene["action"]
        )

        # Step 4: 配音（每句对话）
        audio_parts = []
        for line in scene["dialogue"]:
            audio = synthesize_voice(
                text=line["text"],
                ref_audio=f"refs/{line['speaker']}.wav",
                output_path=f"audio/{scene_id}_{line['speaker']}.wav"
            )
            audio_parts.append(audio)

        # Step 5: 合并音视频
        merge_audio_video(video_path, audio_parts, scene_id)

    # Step 6: 合并所有场景
    concat_scenes(len(scenes), episode_num)
    add_subtitles(episode_num)
```

---

## 工具链汇总

| 步骤 | 工具 | 接口类型 | 费用 |
|------|------|---------|------|
| 剧本生成 | Claude API | REST API | 按 token |
| 分镜生图 | ComfyUI | 本地 REST (`:8188`) | 免费（本地） |
| 角色一致性 | IP-Adapter (ComfyUI 内置) | 同上 | 免费 |
| 图生视频 | Kling API | 云端 REST | ~¥0.7/5s |
| 图生视频（备选） | Wan2.1 | CLI | 免费（本地） |
| 语音克隆 | GPT-SoVITS v3 | 本地 REST (`:9880`) | 免费 |
| 语音克隆（备选） | Fish Speech | Docker REST (`:8080`) | 免费 |
| 音视频合成 | FFmpeg | CLI | 免费 |
| 字幕生成 | WhisperX | CLI | 免费 |

---

## 成本估算（单集 10 分钟，约 60 个场景）

| 项目 | 计算 | 费用 |
|------|------|------|
| 剧本（Claude API） | ~20k tokens | ¥3 |
| 生图（ComfyUI 本地） | 60 张 | ¥0 |
| 视频（Kling，60段×5s） | 300s × ¥0.14 | ¥42 |
| 配音（GPT-SoVITS 本地） | 本地运行 | ¥0 |
| FFmpeg / WhisperX | CLI 工具 | ¥0 |
| **合计** | | **~¥45/集** |

---

## 关键文档链接

- [ComfyUI API 编程指南](https://comfyui.org/en/programmatic-image-generation-api-workflow)
- [ComfyUI Python API 完整教程](https://medium.com/@next.trail.tech/how-to-use-comfyui-api-with-python-a-complete-guide-f786da157d37)
- [可灵 Kling 开发者文档](https://app.klingai.com/cn/dev/document-api/quickStart/productIntroduction/overview)
- [GPT-SoVITS GitHub（含 API 启动说明）](https://github.com/RVC-Boss/GPT-SoVITS)
- [Fish Speech Docker API Server](https://github.com/EvilFreelancer/docker-fish-speech-server)
- [WaveSpeedAI 统一 API（支持 Kling/Wan/Seedance）](https://wavespeed.ai)
- [AI 视频 API 定价对比 2026](https://devtk.ai/en/blog/ai-video-generation-pricing-2026/)
- [ComfyUI Workflow JSON 资源库](https://github.com/Jeff-Emmett/ComfyUI_Workflows)
