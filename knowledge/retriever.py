"""
知识检索 - 从本地 JSON / 歌词库中查找信息
"""
import json
import random
from pathlib import Path
from typing import Optional
from config import KNOWLEDGE_DIR, LYRICS_DIR


class WangKnowledgeBase:
    """汪苏泷知识库"""

    def __init__(self):
        self.discography = self._load_json("discography.json")
        self.fun_facts = self._load_json("fun_facts.json")

    # ────────── 基础方法 ──────────

    def _load_json(self, filename: str) -> list | dict:
        path = KNOWLEDGE_DIR / filename
        if not path.exists():
            return [] if filename == "fun_facts.json" else {}
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    # ────────── 检索方法 ──────────

    def get_overview(self) -> str:
        """生成歌手简介"""
        if not self.discography:
            return "汪苏泷，中国内地男歌手、词曲创作人，代表作《有点甜》《不分手的恋爱》《万有引力》等。"
        a = self.discography.get("artist", {})
        albums = self.discography.get("albums", [])
        songs = self.discography.get("notable_songs", [])
        lines = [
            f"汪苏泷（{a.get('english_name', 'Silence Wang')}），"
            f"{a.get('birth', '1989年')}出生，{a.get('debut', 2010)}年出道。",
            f"风格：{'/'.join(a.get('style', ['华语流行']))}",
            f"专辑数：{len(albums)}张",
            f"代表曲目：{'、'.join(s['name'] for s in songs[:6])}",
        ]
        return "\n".join(lines)

    def search_songs(self, keyword: str) -> list[dict]:
        """按关键词搜索歌曲（歌名、专辑名、主题）"""
        results = []
        songs = self.discography.get("notable_songs", [])
        albums = self.discography.get("albums", [])

        # 从 notable_songs 搜
        for s in songs:
            if keyword.lower() in s["name"].lower():
                results.append(s)

        # 从专辑里的歌搜
        for album in albums:
            if keyword.lower() in album["name"].lower():
                for s in album.get("songs", []):
                    if not any(r["name"] == s for r in results):
                        results.append({"name": s, "album": album["name"], "year": album["year"]})
            for s in album.get("songs", []):
                if keyword.lower() in s.lower():
                    if not any(r["name"] == s for r in results):
                        results.append({"name": s, "album": album["name"], "year": album["year"]})

        return results

    def get_album_info(self, album_name: str) -> dict | None:
        """获取专辑详情"""
        for album in self.discography.get("albums", []):
            if album_name in album["name"]:
                return album
        return None

    def get_random_fact(self) -> str:
        """随机获取一条冷知识"""
        if not self.fun_facts:
            return "最近在忙着写新歌，具体还不能说太多哈~"
        fact = random.choice(self.fun_facts)
        return f"【{fact.get('type', '小故事')}】{fact.get('title', '')}\n{fact.get('content', '')}"

    def get_facts_by_type(self, fact_type: str) -> list:
        """按类型获取冷知识"""
        return [f for f in self.fun_facts if f.get("type") == fact_type]

    def load_lyric(self, song_name: str) -> str | None:
        """加载歌词文件"""
        # 尝试多个可能的文件名
        candidates = [
            LYRICS_DIR / f"{song_name}.txt",
            LYRICS_DIR / f"{song_name}.lrc",
        ]
        for path in candidates:
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    return f.read()
        return None

    def all_song_names(self) -> list[str]:
        """获取所有歌曲名"""
        names = set()
        for s in self.discography.get("notable_songs", []):
            names.add(s["name"])
        for album in self.discography.get("albums", []):
            for s in album.get("songs", []):
                names.add(s)
        return sorted(names)
