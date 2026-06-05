"""
语音合成模块 - Edge-TTS（微软免费 TTS，纯 CPU，无需 API Key）
"""
import os
import asyncio
import edge_tts
from config import TTS_VOICE, AUDIO_DIR


class TTSEngine:
    """语音合成引擎"""

    def __init__(self, voice: str = TTS_VOICE):
        self.voice = voice

    def speak(self, text: str, filename: str = "greeting") -> str:
        """
        将文本转为语音，返回音频文件路径

        Args:
            text: 要朗读的文本
            filename: 输出文件名（不含扩展名）

        Returns:
            音频文件绝对路径
        """
        output_path = str(AUDIO_DIR / f"{filename}.mp3")

        try:
            asyncio.run(self._generate(text, output_path))
            return output_path
        except Exception as e:
            # 如果 edge-tts 报错，回退到提示
            return f"语音生成失败：{e}。你可以试试自己朗读这段文字。"

    async def _generate(self, text: str, output_path: str):
        """异步调用 edge-tts"""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)

    def list_voices(self):
        """列出可用中文语音"""
        try:
            voices = asyncio.run(edge_tts.list_voices())
            cn_voices = [
                v for v in voices
                if "CN" in v["Locale"] or "zh" in v["Locale"]
            ]
            return [
                f"{v['ShortName']} - {v['Gender']} - {v['Locale']}"
                for v in cn_voices
            ]
        except Exception as e:
            return [f"获取语音列表失败：{e}"]
