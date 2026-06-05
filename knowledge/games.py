"""
歌词互动游戏 - 猜歌名 / 接龙 / 补全歌词
"""
import random
import re

from knowledge.retriever import WangKnowledgeBase


class LyricGame:
    """歌词游戏引擎"""

    def __init__(self):
        self.kb = WangKnowledgeBase()

    # ────────── 游戏 1：猜歌名 ──────────

    def guess_song(self) -> dict:
        """给出歌词片段，让用户猜歌名"""
        song_name = random.choice(self.kb.all_song_names())
        lyric = self.kb.load_lyric(song_name)
        if not lyric:
            return {"question": f"提示：这是一首汪苏泷的歌，歌名{song_name[0]}字开头", "answer": song_name}

        lines = [l.strip() for l in lyric.split("\n") if l.strip() and not l.startswith("标题")]
        if len(lines) < 4:
            return {"question": f"提示：这首歌叫《{song_name[0]}...》", "answer": song_name}

        # 取副歌部分（通常重复最多的段落）
        from collections import Counter
        line_freq = Counter(lines)
        chorus_candidate = line_freq.most_common(1)[0][0]

        # 隐藏歌名
        hint = chorus_candidate
        for word in song_name:
            if word in hint:
                hint = hint.replace(word, "＿")

        return {
            "question": f"猜歌名🎵：\n「{hint}」\n（打一首汪苏泷的歌）",
            "answer": song_name,
        }

    def check_guess(self, question: str, user_answer: str, correct_answer: str) -> str:
        """验证猜歌答案"""
        if user_answer.strip() == correct_answer:
            return f"🎉 对了！就是《{correct_answer}》！你也是老粉了吧！"
        # 模糊匹配
        if correct_answer in user_answer or user_answer in correct_answer:
            return f"接近了！是《{correct_answer}》哦，再听听看~"
        return f"不对哦，是《{correct_answer}》，建议循环播放三遍！"

    # ────────── 游戏 2：歌词接龙 ──────────

    def get_chain_start(self) -> dict:
        """出题：给出一句歌词的最后一个字，让用户接"""
        all_songs = self.kb.all_song_names()
        song = random.choice(all_songs)
        lyric = self.kb.load_lyric(song)
        if not lyric:
            # 没有歌词文件，用歌名最后一个字出题
            last_char = song[-1]
            return {"last_char": last_char, "hint": f"以「{last_char}」开头接一句歌词吧"}

        lines = [l.strip() for l in lyric.split("\n") if l.strip() and len(l.strip()) > 4]
        if not lines:
            return {"last_char": "爱", "hint": "以「爱」开头接一句歌词吧"}

        chosen = random.choice(lines)
        last_char = chosen[-1]

        return {
            "last_char": last_char,
            "hint": f"我唱：「{chosen}」\n你用「{last_char}」开头接下一句！",
            "original_line": chosen,
        }

    # ────────── 游戏 3：补全歌词 ──────────

    def fill_blank(self) -> dict:
        """挖空一句歌词让用户填"""
        song_name = random.choice(self.kb.all_song_names())
        lyric = self.kb.load_lyric(song_name)
        if not lyric:
            return {"question": "《" + song_name + "》的歌词还没录入，换首歌吧~", "answer": ""}

        lines = [l.strip() for l in lyric.split("\n")
                 if l.strip() and not l.startswith("标题") and not l.startswith("作词")
                 and not l.startswith("作曲") and len(l.strip()) > 6]
        if len(lines) < 4:
            return {"question": f"提示：这首歌的第一句是「{song_name}」", "answer": ""}

        chosen = random.choice(lines)
        words = list(chosen)

        # 挖掉中间 2-4 个字
        if len(words) < 6:
            blank_len = 2
        else:
            blank_len = random.randint(2, min(4, len(words) - 2))

        start = random.randint(1, max(1, len(words) - blank_len - 1))
        blank_chars = "".join(words[start:start + blank_len])
        words[start:start + blank_len] = ["＿"] * blank_len

        return {
            "question": f"补全歌词🎤：\n「{''.join(words)}」\n—— 《{song_name}》",
            "answer": blank_chars,
            "song": song_name,
        }

    def check_fill(self, question: str, user_answer: str, correct_answer: str) -> str:
        """验证补全答案"""
        if user_answer.strip() == correct_answer:
            return "🎯 完全正确！你怕不是把歌词背下来了吧！"
        if correct_answer in user_answer or user_answer in correct_answer:
            return f"差不多对了！正确答案是「{correct_answer}」~"
        return f"不对哦，是「{correct_answer}」。再听一遍！"
