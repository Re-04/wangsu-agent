"""
音乐播放模块 - 歌曲查找 + 播放链接
=====================================
直接从内置列表查找歌曲，返回网易云外链播放URL
不调网易云API（魔搭服务器会被拦截），全用离线匹配
"""
from typing import Optional


class MusicPlayer:
    """歌曲查找与播放器"""

    def __init__(self):
        # 内置汪苏泷热门歌曲（含已知网易云ID）
        self.builtin_songs = [
            {"name": "有点甜", "artist": "汪苏泷/BY2", "id": 27759674},
            {"name": "万有引力", "artist": "汪苏泷", "id": 27759677},
            {"name": "不分手的恋爱", "artist": "汪苏泷", "id": 27759672},
            {"name": "小星星", "artist": "汪苏泷", "id": 27759673},
            {"name": "风度", "artist": "汪苏泷", "id": 27759676},
            {"name": "花千骨", "artist": "汪苏泷", "id": 35565752},
            {"name": "年轮", "artist": "汪苏泷", "id": 406008706},
            {"name": "追光者", "artist": "汪苏泷", "id": 515206562},
            {"name": "大娱乐家", "artist": "汪苏泷", "id": 1902731557},
            {"name": "苦笑", "artist": "汪苏泷", "id": 27759671},
            {"name": "三国杀", "artist": "汪苏泷", "id": 27759669},
            {"name": "巴赫旧约", "artist": "汪苏泷", "id": 27759670},
            {"name": "埋葬冬天", "artist": "汪苏泷", "id": 27759675},
            {"name": "那一年", "artist": "汪苏泷", "id": 27759678},
            {"name": "脑海", "artist": "汪苏泷", "id": 27759679},
            {"name": "唯你懂我心", "artist": "汪苏泷", "id": 27759680},
            {"name": "幸福是被你需要", "artist": "汪苏泷", "id": 27759681},
            {"name": "慢慢懂", "artist": "汪苏泷", "id": 27759682},
            {"name": "专属味道", "artist": "汪苏泷", "id": 29141051},
            {"name": "第一首情歌", "artist": "汪苏泷", "id": 27759683},
        ]

    # ── 查找（纯本地，不调API） ──

    def search(self, keyword: str, limit: int = 10) -> list:
        """从内置列表模糊查找歌曲"""
        kw = keyword.strip().lower().replace(" ", "")
        if not kw:
            return self.builtin_songs[:limit]

        results = []
        seen = set()
        for s in self.builtin_songs:
            # 精确匹配 > 包含匹配
            name_key = s["name"].lower().replace(" ", "")
            artist_key = s["artist"].lower()
            if kw == name_key or kw in name_key or kw in artist_key:
                dedup_key = f"{s['name']}_{s['artist']}"
                if dedup_key not in seen:
                    seen.add(dedup_key)
                    results.append(s)
            if len(results) >= limit:
                break

        # 没找到时也返回一点默认结果
        if not results:
            return self.builtin_songs[:limit]
        return results

    # ── 播放URL ──

    def get_play_url(self, song_id: int) -> str:
        """网易云音乐外链播放URL"""
        return f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"

    def get_player_html(self, song_name: str) -> str:
        """
        直接根据歌名生成 HTML 播放器
        返回整段 HTML，webui 直接用
        """
        results = self.search(song_name)
        if not results:
            return (
                f'<div style="text-align:center;padding:20px;color:red;">'
                f'未找到「{song_name}」，试试：有点甜、万有引力、小星星...</div>'
            )

        song = results[0]
        audio_url = self.get_play_url(song["id"])
        name = song["name"]
        artist = song["artist"]

        sid = song["id"]
        return (
            f'<div style="text-align:center;padding:20px;'
            f'background:linear-gradient(135deg,#667eea,#764ba2);'
            f'border-radius:16px;color:white;">'
            f'<p style="font-size:20px;font-weight:bold;margin-bottom:5px;">'
            f'🎵 {name}</p>'
            f'<p style="font-size:14px;margin-bottom:15px;opacity:0.9;">{artist}</p>'
            f'<audio controls autoplay style="width:100%;max-width:400px;">'
            f'<source src="{audio_url}" type="audio/mpeg">'
            f'</audio>'
            f'<p style="font-size:12px;margin-top:10px;opacity:0.7;">'
            f'若无法播放，<a href="https://music.163.com/#/song?id={sid}" '
            f'target="_blank" style="color:white;text-decoration:underline;">'
            f'点此在网易云打开</a></p></div>'
        )

    # ── 心情推荐 ──

    def get_recommendations(self, mood: str) -> list:
        """根据心情推荐内置歌曲"""
        mood_map = {
            "开心": ["有点甜", "万有引力", "专属味道", "幸福是被你需要"],
            "失恋": ["苦笑", "不分手的恋爱", "风度", "那一年"],
            "怀旧": ["小星星", "慢慢懂", "三国杀", "巴赫旧约"],
            "甜蜜": ["有点甜", "专属味道", "幸福是被你需要", "唯你懂我心"],
            "安静": ["慢慢懂", "脑海", "唯你懂我心", "埋葬冬天"],
        }
        for key, song_names in mood_map.items():
            if key in mood:
                return [s for s in self.builtin_songs if s["name"] in song_names]
        return self.builtin_songs[:5]
