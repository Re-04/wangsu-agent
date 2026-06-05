# 🎵 汪苏泷 AI Agent

> 一个以歌手汪苏泷为原型的 AI 交互助手，支持闲聊对话、歌词游戏、音乐分析、文案创作等功能。

---

## ✨ 功能一览

| 模块 | 功能 | 说明 |
|------|------|------|
| 🗣 **拟人对话** | 粉丝闲聊 | 以汪苏泷语气聊天，聊创作、玩梗 |
| | 歌曲科普 | 第一人称讲解歌曲创作思路 |
| | 冷知识 | 分享采访趣闻、幕后故事 |
| 🎮 **歌词游戏** | 猜歌名 | 给歌词片段猜歌名 |
| | 补全歌词 | 挖空歌词让你填 |
| | 歌词接龙 | 末字接龙 |
| ✍️ **创作生成** | 歌词创作 | 汪苏泷风格写新歌词 |
| | 文案生成 | 朋友圈/短视频/乐评 |
| | 智能推歌 | 根据心情推荐歌曲 |
| 🎵 **音乐分析** | 歌曲分析 | BPM/调式/和弦提取 |
| | AI 讲解 | AI 以汪苏泷口吻讲解创作思路 |
| | 人声分离 | HPSS 轻量分离人声/伴奏 |
| 🔊 **语音** | 语音祝福 | Edge-TTS 生成语音祝福 |

---

## 🚀 快速开始

### 1. 安装

```bash
pip install -r requirements.txt
```

### 2. 设置 API Key

```bash
# Windows (CMD)
set DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx

# Windows (PowerShell)
$env:DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"

# Mac / Linux
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
```

> 没有 Key？去 [platform.deepseek.com](https://platform.deepseek.com) 注册获取

### 3. 运行

**CLI 模式（推荐先试试这个）**：
```bash
python main.py
```

**Web 界面（推荐日常使用）**：
```bash
python webui.py
```

浏览器打开 http://127.0.0.1:7860

---

## 📁 数据准备

项目已包含模板数据，可以直接运行。如果想自己补充更多数据：

| 文件 | 内容 | 如何获取 |
|------|------|----------|
| `knowledge/data/discography.json` | 专辑、歌曲信息 | 百度百科/QQ音乐整理 |
| `knowledge/data/lyrics/*.txt` | 歌词原文 | 网易云音乐/QQ音乐复制 |
| `knowledge/data/fun_facts.json` | 采访趣闻 | 访谈视频/B站整理 |

---

## 🧩 项目结构

```
wangsu-agent/
├── main.py              # CLI 入口
├── webui.py             # Gradio 网页入口
├── config.py            # 全局配置
├── requirements.txt     # 依赖清单
├── agent/
│   ├── core.py          # Agent 主循环（DeepSeek API）
│   └── tools.py         # 工具调度
├── knowledge/
│   ├── data/            # JSON + 歌词数据
│   ├── retriever.py     # 知识检索
│   └── games.py         # 歌词游戏
├── music/
│   ├── analyzer.py      # Librosa 音频分析
│   ├── tts.py           # Edge-TTS 语音合成
│   └── separation.py    # HPSS 人声分离
├── generation/
│   ├── lyric_gen.py     # 歌词生成
│   └── copywrite.py     # 文案生成
├── prompts/
│   └── templates.py     # 人设 + 场景 Prompt
└── utils/
    └── audio.py         # 音频工具
```

---

## 🔧 技术栈

- **LLM**：DeepSeek API（OpenAI 兼容接口）
- **音频分析**：Librosa（纯 CPU）
- **语音合成**：Edge-TTS（微软免费 TTS）
- **网页界面**：Gradio
- **人声分离**：Librosa HPSS

---

## 📌 注意

- 本项目使用 DeepSeek API，需自行申请 API Key
- 音频分析功能纯 CPU 可跑，处理一首 3 分钟的歌大约 1-2 分钟
- 人声分离使用 HPSS 轻量方案，效果不如 Demucs/UVR5，但无需 GPU
