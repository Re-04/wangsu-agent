"""
音乐播放模块 - 歌曲查找 + 播放链接
=====================================
多路公共 API 搜索，一路不行自动换下一路
全部失败时回退到内置歌曲列表
"""
import requests
import urllib3
from typing import Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === 免费公共网易云音乐接口（多路备用） ===
API_LIST = [
    {
        "name": "liyaoyu",
        "url": "https://music.liyaoyu.top/search",
        "params": lambda kw, limit: {"keywords": kw, "limit": limit},
        "parse": lambda data: data.get("result", {}).get("songs", []),
    },
    {
        "name": "66mz8",
        "url": "https://api.66mz8.com/api/music.163.php",
        "params": lambda kw, limit: {"type": "search", "name": kw, "n": limit},
        "parse": lambda data: data if isinstance(data, list) else data.get("data", []),
    },
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


class MusicPlayer:
    """歌曲查找与播放器"""

    def __init__(self):
        # 内置汪苏泷热门歌曲（API 全失败时的备选）
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

    # ── 搜索（多路API → 内置备选） ──

    def search(self, keyword: str, limit: int = 5) -> list:
        """搜索歌曲，自动切换备用API"""
        results = self._search_all_apis(keyword, limit)
        if results:
            return results
        return self._search_builtin(keyword, limit)

    def _search_all_apis(self, keyword: str, limit: int = 5) -> list:
        """挨个尝试所有公共API"""
        for api in API_LIST:
            try:
                resp = requests.get(
                    api["url"],
                    params=api["params"](keyword, limit),
                    headers=HEADERS,
                    timeout=8,
                    verify=False,
                )
                if resp.status_code != 200:
                    continue

                data = resp.json()
                raw_songs = api["parse"](data)
                if not raw_songs:
                    continue

                songs = []
                for item in raw_songs:
                    # 兼容不同API的返回格式
                    song_id = item.get("id") or item.get("song_id")
                    song_name = item.get("name") or item.get("song_name")
                    artists_data = item.get("artists") or item.get("artist") or []
                    if isinstance(artists_data, str):
                        artist_name = artists_data
                    elif isinstance(artists_data, list):
                        artist_name = ", ".join(
                            a.get("name", "") for a in artists_data if isinstance(a, dict)
                        )
                    else:
                        artist_name = "未知"

                    if song_id and song_name:
                        songs.append({
                            "name": song_name,
                            "artist": artist_name or "未知",
                            "id": int(song_id) if not isinstance(song_id, int) else song_id,
                        })
                if songs:
                    return songs[:limit]
            except Exception:
                continue
        return []

    def _search_builtin(self, keyword: str, limit: int = 5) -> list:
        """从内置列表模糊查找"""
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
        return results if results else self.builtin_songs[:limit]

    # ── 播放器 ──

    def get_play_url(self, song_id: int) -> str:
        return f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"

    def get_player_html(self, song_name: str) -> str:
        """根据歌名生成 HTML 播放器"""
        results = self.search(song_name)
        if not results:
            return (
                '<div style="text-align:center;padding:30px;color:#999;">'
                f'未找到「{song_name}」<br>'
                f'试试内置歌单：有点甜、万有引力、小星星...</div>'
            )

        song = results[0]
        sid = song["id"]
        audio_url = self.get_play_url(sid)
        netease_url = f"https://music.163.com/#/song?id={sid}"

        return (
            '<div style="text-align:center;padding:20px;'
            'background:linear-gradient(135deg,#667eea,#764ba2);'
            'border-radius:16px;color:white;">'
            f'<p style="font-size:20px;font-weight:bold;margin-bottom:5px;">'
            f'🎵 {song["name"]}</p>'
            f'<p style="font-size:14px;margin-bottom:15px;opacity:0.9;">'
            f'{song["artist"]}</p>'
            f'<audio controls autoplay style="width:100%;max-width:400px;">'
            f'<source src="{audio_url}" type="audio/mpeg">'
            f'</audio>'
            f'<p style="font-size:12px;margin-top:10px;opacity:0.7;">'
            f'若无法播放，'
            f'<a href="{netease_url}" target="_blank" '
            f'style="color:white;text-decoration:underline;">'
            f'点此在网易云打开</a></p></div>'
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
