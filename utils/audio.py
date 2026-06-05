"""
音频工具函数 - 格式转换、播放等辅助功能
"""
import os
import subprocess
from pathlib import Path
from config import AUDIO_DIR


def convert_to_wav(input_path: str, target_sr: int = 22050) -> str:
    """
    将各种音频格式统一转换为 WAV（16kHz/22.05kHz 单声道）

    Args:
        input_path: 输入文件路径
        target_sr: 目标采样率

    Returns:
        转换后的 WAV 文件路径
    """
    import soundfile as sf
    import librosa

    y, sr = librosa.load(input_path, sr=target_sr, mono=True)
    output_path = str(AUDIO_DIR / f"{Path(input_path).stem}_converted.wav")
    sf.write(output_path, y, target_sr)
    return output_path


def get_audio_duration(audio_path: str) -> float:
    """获取音频时长（秒）"""
    import librosa
    try:
        duration = librosa.get_duration(path=audio_path)
        return round(duration, 2)
    except Exception:
        return 0.0


def play_audio(audio_path: str):
    """播放音频文件（调用系统播放器）"""
    if not os.path.exists(audio_path):
        print(f"文件不存在：{audio_path}")
        return

    system = os.name
    try:
        if system == "nt":  # Windows
            os.startfile(audio_path)
        elif system == "posix":  # Mac / Linux
            subprocess.run(["xdg-open", audio_path], check=False)
        else:
            print(f"音频文件：{audio_path}")
    except Exception as e:
        print(f"播放失败：{e}，文件路径：{audio_path}")


def list_audio_files(directory: str = None) -> list[str]:
    """列出目录下的音频文件"""
    if directory is None:
        directory = str(AUDIO_DIR)
    if not os.path.exists(directory):
        return []

    exts = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"}
    return sorted([
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if Path(f).suffix.lower() in exts
    ])
