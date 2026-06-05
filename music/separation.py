"""
人声分离模块 - HPSS 轻量方案（纯 CPU 可跑）

将音频分离为 人声（谐波） + 伴奏（打击乐）

注意：HPSS 是轻量算法，分离质量不如 Demucs/UVR5
但胜在不需要 GPU，也没有复杂的模型依赖
"""
import os
import librosa
import soundfile as sf
from config import SAMPLE_RATE, AUDIO_DIR


class AudioSeparator:
    """音频分离器"""

    def separate(self, audio_path: str) -> dict:
        """
        分离人声和伴奏

        Returns:
            {
                "vocal_path": "xxx_vocal.wav",
                "instrumental_path": "xxx_instrumental.wav",
                "success": True/False,
                "error": "错误信息"
            }
        """
        if not os.path.exists(audio_path):
            return {"success": False, "error": f"文件不存在：{audio_path}"}

        try:
            y, sr = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)

            # HPSS 分离
            y_harmonic, y_percussive = librosa.effects.hpss(y)

            base = os.path.splitext(os.path.basename(audio_path))[0]

            # 保存人声（谐波部分 ≈ 人声 + 旋律乐器）
            vocal_path = str(AUDIO_DIR / f"{base}_vocal.wav")
            sf.write(vocal_path, y_harmonic, sr)

            # 保存伴奏（打击乐部分 ≈ 节奏 + 伴奏）
            inst_path = str(AUDIO_DIR / f"{base}_instrumental.wav")
            sf.write(inst_path, y_percussive, sr)

            return {
                "success": True,
                "vocal_path": vocal_path,
                "instrumental_path": inst_path,
                "note": "HPSS 轻量分离，质量有限，建议配合 UVR5 获得更好效果（需 GPU）"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def batch_separate(self, audio_dir: str) -> list[dict]:
        """批量分离文件夹中所有音频"""
        results = []
        for fname in os.listdir(audio_dir):
            if fname.lower().endswith((".mp3", ".wav", ".m4a", ".flac")):
                path = os.path.join(audio_dir, fname)
                result = self.separate(path)
                results.append(result)
        return results
