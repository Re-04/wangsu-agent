"""
汪苏泷 AI Agent - 全局配置
"""
import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent

# ===== DeepSeek API 配置 =====
# 使用方式：export DEEPSEEK_API_KEY="sk-xxx"
# 或者在代码里直接填写（不推荐提交到 Git）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

# ===== 数据路径 =====
KNOWLEDGE_DIR = ROOT_DIR / "knowledge" / "data"
LYRICS_DIR = KNOWLEDGE_DIR / "lyrics"
AUDIO_DIR = ROOT_DIR / "audio_cache"

# 确保目录存在
AUDIO_DIR.mkdir(exist_ok=True)

# ===== 音频配置 =====
SAMPLE_RATE = 22050

# Edge-TTS 语音（中文男声）
TTS_VOICE = "zh-CN-YunxiNeural"

# ===== 生成配置 =====
MAX_TOKENS = 4096
TEMPERATURE = 0.8
