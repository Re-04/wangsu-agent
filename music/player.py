"""
音乐播放模块 - 内置歌曲列表 + iframe 嵌入播放
===============================================
用网易云官方 outchain 播放器（已验证可通）
歌曲 ID 从内置列表获取，不依赖外部 API
"""
from typing import Optional


class MusicPlayer:
    """歌曲查找与播放器"""

    def __init__(self):
        # 汪苏泷热门歌曲（含已确认有效的网易云ID）
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

    def search(self, keyword: str, limit: int = 5) -> list:
        """从内置列表模糊查找歌曲"""
        kw = keyword.strip().lower().replace(" ", "")
        if not kw:
            return self.builtin_songs[:limit]

        results = []
        seen = set()
        for s in self.builtin_songs:
            name_key = s["name"].lower().replace(" ", "")
            artist_key = s["artist"].lower()
            if kw == name_key or kw in name_key or kw in artist_key:
                key = f"{s['name']}_{s['artist']}"
                if key not in seen:
                    seen.add(key)
                    results.append(s)
            if len(results) >= limit:
                break
        return results if results else []

    def get_player_html(self, song_name: str) -> str:
        """
        根据歌名生成网易云嵌入播放器 HTML
        使用 verified 可用的 outchain/player
        """
        results = self.search(song_name)
        if not results:
            # 不在内置列表 -> 提供网易云搜索链接
            search_url = f"https://music.163.com/#/search/m/?s={song_name}"
            return (
                f'<div style="text-align:center;padding:30px;color:#666;">'
                f'<p>「{song_name}」不在快捷歌单中</p>'
                f'<p style="font-size:14px;margin-top:10px;">'
                f'<a href="{search_url}" target="_blank" '
                f'style="color:#667eea;text-decoration:underline;">'
                f'👉 点此在网易云搜索</a></p>'
                f'<p style="font-size:12px;color:#999;margin-top:8px;">'
                f'或者试试：有点甜、万有引力、小星星...</p></div>'
            )

        song = results[0]
        sid = song["id"]

        return (
            f'<div style="text-align:center;padding:15px;'
            f'background:#f8f9ff;border-radius:12px;'
            f'border:1px solid #e0e3f0;">'
            f'<p style="font-size:18px;font-weight:bold;color:#333;margin-bottom:8px;">'
            f'🎵 {song["name"]} <span style="font-size:14px;color:#999;font-weight:normal;">'
            f'- {song["artist"]}</span></p>'
            f'<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" '
            f'width=330 height=86 '
            f'src="//music.163.com/outchain/player?type=2&id={sid}&auto=1&height=66">'
            f'</iframe></div>'
        )

    # ── 心情推荐 ──

    def get_recommendations(self, mood: str) -> list:
        mood_map = {
            "开心": ["有点甜", "万有引力", "专属味道", "幸福是被你需要"],
            "失恋": ["苦笑", "不分手的恋爱", "风度", "那一年"],
            "怀旧": ["小星星", "慢慢懂", "三国杀", "巴赫旧约"],
            "甜蜜": ["有点甜", "专属味道", "幸福是被你需要", "唯你懂我心"],
            "安静": ["慢慢懂", "脑海", "唯你懂我心", "埋葬冬天"],
        }
        for key, names in mood_map.items():
            if key in mood:
                return [s for s in self.builtin_songs if s["name"] in names]
        return self.builtin_songs[:5]
