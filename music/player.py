"""
音乐播放模块 - 歌曲搜索 + 播放链接生成
=========================================
基于网易云音乐公开 API，无需 API Key

搜索歌曲 → 获得歌曲 ID → 生成可嵌入播放器
"""
import re
import json
import requests
import urllib.parse
from typing import Optional


# 网易云音乐 API
SEARCH_URL = "https://music.163.com/api/search/pc"
SONG_URL = "https://music.163.com/api/song/detail"
PLAYER_TPL = (
    '<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" '
    'width=330 height=86 '
    'src="//music.163.com/outchain/player?type=2&id={song_id}&auto=1&height=66">'
    '</iframe>'
)

# 汪苏泷热门歌单（网易云歌单ID，方便一键播放）
DEFAULT_PLAYLISTS = {
    "汪苏泷热门50首": "530739351",
    "汪苏泷·经典情歌": "2659807983",
    "汪苏泷·全部歌曲": "2474913662",
}


class MusicPlayer:
    """歌曲搜索与播放器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://music.163.com/",
        })
        # 内置汪苏泷热门歌曲（搜索失败时的备选）
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
            {"name": "有点甜", "artist": "汪苏泷/BY2", "id": 27759674},
            {"name": "埋葬冬天", "artist": "汪苏泷", "id": 27759675},
            {"name": "那一年", "artist": "汪苏泷", "id": 27759678},
            {"name": "脑海", "artist": "汪苏泷", "id": 27759679},
            {"name": "唯你懂我心", "artist": "汪苏泷", "id": 27759680},
            {"name": "幸福是被你需要", "artist": "汪苏泷", "id": 27759681},
            {"name": "慢慢懂", "artist": "汪苏泷", "id": 27759682},
            {"name": "专属味道", "artist": "汪苏泷", "id": 29141051},
        ]
        # 建立快速查找索引
        self._name_index = {}
        for s in self.builtin_songs:
            key = s["name"].lower().replace(" ", "")
            self._name_index[key] = s

    # ── 搜索 ──

    def search(self, keyword: str, limit: int = 10) -> list:
        """
        搜索歌曲（优先调网易云API，失败用内置列表）

        Returns:
            [{"name": "...", "artist": "...", "id": 123, "album": "..."}, ...]
        """
        results = self._search_netease(keyword, limit)
        if results:
            return results
        # API 失败，从内置列表模糊匹配
        return self._search_builtin(keyword, limit)

    def _search_netease(self, keyword: str, limit: int = 10) -> list:
        """调网易云 API 搜索"""
        try:
            params = {
                "s": keyword,
                "type": 1,        # 1=歌曲
                "offset": 0,
                "limit": limit,
            }
            resp = self.session.get(
                SEARCH_URL,
                params=params,
                timeout=10,
            )
            data = resp.json()
            if data.get("code") != 200:
                return []

            songs = []
            for item in data.get("result", {}).get("songs", []):
                artists = ", ".join(a["name"] for a in item.get("artists", []))
                songs.append({
                    "name": item["name"],
                    "artist": artists,
                    "id": item["id"],
                    "album": item.get("album", {}).get("name", ""),
                    "duration": item.get("duration", 0) // 1000,  # 转秒
                })
            return songs

        except Exception:
            return []

    def _search_builtin(self, keyword: str, limit: int = 10) -> list:
        """从内置列表模糊搜索"""
        kw = keyword.lower().replace(" ", "")
        results = []
        for s in self.builtin_songs:
            if kw in s["name"].lower().replace(" ", "") or kw in s["artist"]:
                if s not in results:
                    results.append(s)
            if len(results) >= limit:
                break
        return results

    # ── 播放 ──

    def get_embed_html(self, song_id: int) -> str:
        """生成网易云嵌入播放器 HTML"""
        return PLAYER_TPL.format(song_id=song_id)

    def get_play_url(self, song_id: int) -> str:
        """获取可直接播放的 URL"""
        return f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"

    def get_song_detail(self, song_id: int) -> Optional[dict]:
        """获取歌曲详细信息"""
        try:
            params = {"id": song_id, "ids": f"[{song_id}]"}
            resp = self.session.get(SONG_URL, params=params, timeout=10)
            data = resp.json()
            if data.get("code") == 200 and data.get("songs"):
                s = data["songs"][0]
                return {
                    "name": s["name"],
                    "artist": ", ".join(a["name"] for a in s.get("artists", [])),
                    "album": s.get("album", {}).get("name", ""),
                    "pic": s.get("album", {}).get("picUrl", ""),
                }
        except Exception:
            pass
        return None

    # ── 歌单 ──

    def get_playlist_embed(self, playlist_id: str) -> str:
        """生成歌单嵌入播放器"""
        return (
            f'<iframe frameborder="no" border="0" marginwidth="0" '
            f'marginheight="0" width=330 height=450 '
            f'src="//music.163.com/outchain/player?type=0&id={playlist_id}'
            f'&auto=1&height=430">'
            f'</iframe>'
        )

    def get_recommendations(self, mood: str) -> list:
        """根据心情推荐内置歌曲"""
        mood_map = {
            "开心": ["有点甜", "万有引力", "专属味道", "幸福是被你需要"],
            "失恋": ["苦笑", "不分手的恋爱", "风度", "那一年"],
            "怀旧": ["小星星", "慢慢懂", "三国杀", "巴赫旧约"],
            "甜蜜": ["有点甜", "专属味道", "幸福是被你需要", "唯你懂我心"],
            "安静": ["慢慢懂", "脑海", "唯你懂我心", "埋葬冬天"],
        }
        for key, songs in mood_map.items():
            if key in mood:
                return [s for s in self.builtin_songs if s["name"] in songs]
        # 默认返回热门
        return self.builtin_songs[:5]
