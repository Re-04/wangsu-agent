"""
音乐分析模块 - Librosa 纯 CPU 方案

提取：BPM、调式、和弦、人声分离(HPSS)
"""
import os
import numpy as np
import librosa
from config import SAMPLE_RATE, AUDIO_DIR


class MusicAnalyzer:
    """音频文件分析器"""

    # 调式名称映射
    KEY_NAMES = [
        "C", "C#", "D", "D#", "E", "F",
        "F#", "G", "G#", "A", "A#", "B"
    ]

    def full_analysis(self, audio_path: str) -> dict:
        """完整分析一首歌"""
        if not os.path.exists(audio_path):
            return {"error": f"文件不存在：{audio_path}"}

        try:
            # 加载音频
            y, sr = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)

            result = {
                "duration": duration,
                "bpm": self._detect_bpm(y, sr),
                "key": self._detect_key(y, sr),
                "chords": self._detect_chords(y, sr),
            }

            # 尝试 HPSS 人声分离
            try:
                y_harmonic, y_percussive = librosa.effects.hpss(y)
                vocal_path = AUDIO_DIR / f"{os.path.basename(audio_path)}_vocal.wav"
                librosa.output.write_wav(str(vocal_path), y_harmonic, sr)
                result["vocal_separated"] = True
                result["vocal_path"] = str(vocal_path)
            except Exception:
                result["vocal_separated"] = False

            return result

        except Exception as e:
            return {"error": str(e)}

    def _detect_bpm(self, y: np.ndarray, sr: int) -> float:
        """检测 BPM（每分钟节拍数）"""
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return round(float(tempo), 1)

    def _detect_key(self, y: np.ndarray, sr: int) -> str:
        """检测调式"""
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        key_index = int(np.argmax(chroma_mean))
        return self.KEY_NAMES[key_index % 12]

    def _detect_chords(self, y: np.ndarray, sr: int) -> str:
        """检测和弦走向（简化版）"""
        # 计算 chroma 特征
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

        # 分帧，每 4 拍检测一个和弦
        hop_length = 512
        frames = chroma.shape[1]
        chord_list = []

        # 每 8 帧取一个和弦
        step = 8
        for i in range(0, frames, step):
            frame_chroma = np.mean(chroma[:, i:i + step], axis=1)
            root = int(np.argmax(frame_chroma))
            chord_name = self.KEY_NAMES[root % 12]

            # 判断大小调（大三和弦 = 0,4,7 强；小三和弦 = 0,3,7 强）
            major_score = frame_chroma[root] + frame_chroma[(root + 4) % 12] + frame_chroma[(root + 7) % 12]
            minor_score = frame_chroma[root] + frame_chroma[(root + 3) % 12] + frame_chroma[(root + 7) % 12]

            if minor_score > major_score:
                chord_name += "m"

            # 去重
            if not chord_list or chord_list[-1] != chord_name:
                chord_list.append(chord_name)

        # 简化为前 8 个不同和弦
        unique = []
        for c in chord_list:
            if c not in unique:
                unique.append(c)
            if len(unique) >= 8:
                break

        return " → ".join(unique) if unique else "未检测"

    def extract_piano_melody(self, audio_path: str) -> str:
        """
        提取主旋律（近似钢琴独奏）
        输出 MIDI 文件路径
        """
        try:
            y, sr = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)

            # 用 HPSS 提取谐波部分
            y_harmonic, _ = librosa.effects.hpss(y)

            # 基频检测
            f0, voiced_flag, _ = librosa.pyin(
                y_harmonic,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7'),
                sr=sr
            )

            # 转换频率为 MIDI 音符
            midi_notes = []
            for f, v in zip(f0, voiced_flag):
                if v and not np.isnan(f):
                    midi = librosa.hz_to_midi(f)
                    midi_notes.append(int(round(midi)))
                else:
                    midi_notes.append(0)  # 休止符

            # 存为文本格式（而非真正的 MIDI 文件，避免依赖 mido）
            output_path = AUDIO_DIR / f"{os.path.basename(audio_path)}_melody.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"主旋律音符（MIDI 编号）：\n")
                # 只输出前 500 个非零音符
                active = [str(n) for n in midi_notes[:500] if n > 0]
                f.write(", ".join(active))

            return str(output_path)

        except Exception as e:
            return f"旋律提取失败：{e}"

    def analyze_separated_vocal(self, audio_path: str) -> str:
        """
        简单的人声分析（不需要 GPU 分离）
        直接分析原曲的谐波部分特征
        """
        try:
            y, sr = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)
            y_harmonic, _ = librosa.effects.hpss(y)

            # 提取 RMS 能量
            rms = librosa.feature.rms(y=y_harmonic)
            avg_energy = float(np.mean(rms))

            # 零交叉率（粗略判断声音的明亮度）
            zcr = librosa.feature.zero_crossing_rate(y_harmonic)
            avg_zcr = float(np.mean(zcr))

            return (
                f"🎤 人声特征分析：\n"
                f"平均能量：{avg_energy:.4f}\n"
                f"明亮度：{'偏高' if avg_zcr > 0.1 else '偏低'} ({avg_zcr:.3f})\n"
                f"建议：{self._voice_suggestion(avg_energy, avg_zcr)}"
            )
        except Exception as e:
            return f"分析失败：{e}"

    def _voice_suggestion(self, energy: float, zcr: float) -> str:
        """根据特征给出演唱建议"""
        if energy < 0.05:
            return "演唱力度偏轻，可以试试加强气息支撑"
        elif energy > 0.3:
            return "情感很充沛，注意控制不要破音"
        else:
            return "能量适中，保持这个状态"
        # zcr 越高声音越亮
