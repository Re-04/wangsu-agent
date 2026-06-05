"""
音乐播放模块 - 歌曲查找 + 播放链接
=====================================
优先调免费公共网易云API搜索歌曲ID
API 来源：https://music.liyaoyu.top（无需签名，免费可用）
失败时回退到内置歌曲列表
"""
import requests
import urllib3
from typing import Optional

# 关闭 SSL 警告（第三方 API 证书不匹配）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 免费公共网易云音乐接口
API_SEARCH = "https://music.liyaoyu.top/search"
API_SONG = "https://music.liyaoyu.top/song/detail"
HEADERS = {"User-Agent": "Mozilla/5.0"}


class MusicPlayer:
    """歌曲查找与播放器"""

    def __init__(self):
        # 内置汪苏泷热门歌曲（API 失败时的备选）
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

    # ── 搜索（API优先 → 内置备选） ──

    def search(self, keyword: str, limit: int = 5) -> list:
        """搜索歌曲：优先调公共API，失败回退内置列表"""
        results = self._search_api(keyword, limit)
        if results:
            return results
        return self._search_builtin(keyword, limit)

    def _search_api(self, keyword: str, limit: int = 5) -> list:
        """调免费公共网易云 API 搜索"""
        try:
            resp = requests.get(
                API_SEARCH,
                params={"keywords": keyword, "limit": limit},
                headers=HEADERS,
                timeout=10,
                verify=False,   # 第三方API，SSL证书不匹配
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
                })
            return songs
        except Exception:
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
        """网易云音乐外链播放URL"""
        return f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"

    def get_player_html(self, song_name: str) -> str:
        """
        根据歌名查找并生成 HTML 播放器
        """
        results = self.search(song_name)
        if not results:
            return (
                '<div style="text-align:center;padding:30px;color:#999;">'
                f'未找到「{song_name}」的相关结果</div>'
            )

        song = results[0]
        sid = song["id"]
        audio_url = self.get_play_url(sid)

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
            f'<a href="https://music.163.com/#/song?id={sid}" '
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
        for key, names in mood_map.items():
            if key in mood:
                return [s for s in self.builtin_songs if s["name"] in names]
        return self.builtin_songs[:5]
