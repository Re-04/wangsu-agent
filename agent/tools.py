"""
工具调度 - 将所有模块整合到 Agent 可调用的工具集中
"""
import re
from knowledge.retriever import WangKnowledgeBase
from knowledge.games import LyricGame
from music.analyzer import MusicAnalyzer
from music.tts import TTSEngine
from music.player import MusicPlayer
from generation.lyric_gen import LyricGenerator
from generation.copywrite import Copywriter


class AgentTools:
    """Agent 可用的工具集合"""

    def __init__(self, agent):
        self.agent = agent
        self.kb = WangKnowledgeBase()
        self.games = LyricGame()
        self.analyzer = MusicAnalyzer()
        self.tts = TTSEngine()
        self.player = MusicPlayer()
        self.lyric_gen = LyricGenerator(agent)
        self.copywriter = Copywriter(agent)

        # 聊天上下文标记
        self.in_game = False
        self.game_data = {}

    # ══════════════ 模块 1：对话交互 ══════════════

    def handle_chat(self, user_input: str) -> str:
        """普通闲聊（直接走 DeepSeek 人设）"""
        self.in_game = False
        return self.agent.chat(user_input)

    def get_intro(self) -> str:
        """自我介绍"""
        overview = self.kb.get_overview()
        return (
            f"哎~你好你好！我是汪苏泷！\n"
            f"{overview}\n"
            "你可以跟我聊天、玩游戏、分析歌词，或者让我帮你写歌！要试试哪个？"
        )

    def handle_fact(self) -> str:
        """讲个幕后故事"""
        return f"来，跟你分享个事儿——\n{self.kb.get_random_fact()}"

    # ══════════════ 模块 1b：歌词游戏 ══════════════

    def handle_game(self, action: str, user_answer: str = "") -> str:
        """歌词游戏入口"""
        self.in_game = True

        if action == "guess":
            data = self.games.guess_song()
            self.game_data = {"type": "guess", "answer": data["answer"]}
            return data["question"]

        elif action == "fill":
            data = self.games.fill_blank()
            self.game_data = {"type": "fill", "answer": data["answer"], "question": data["question"]}
            return data["question"]

        elif action == "chain":
            data = self.games.get_chain_start()
            self.game_data = {"type": "chain", "last_char": data["last_char"]}
            return data["hint"]

        elif action == "answer" and self.game_data:
            gtype = self.game_data.get("type")
            correct = self.game_data.get("answer", "")
            question = self.game_data.get("question", "")

            if gtype == "guess":
                result = self.games.check_guess(question, user_answer, correct)
            elif gtype == "fill":
                result = self.games.check_fill(question, user_answer, correct)
            else:
                self.in_game = False
                return "游戏结束！想再玩一次吗？"
            self.in_game = False
            return result

        return "想玩什么游戏？猜歌名、补全歌词、歌词接龙，你选一个！"

    # ══════════════ 模块 2：音乐分析 ══════════════

    def analyze_audio(self, audio_path: str) -> str:
        """分析音频文件"""
        result = self.analyzer.full_analysis(audio_path)
        if "error" in result:
            return f"分析出问题了：{result['error']}"

        lines = [
            "🎵 分析结果来啦！",
            f"⏱ 时长：{result.get('duration', 0):.1f}s",
            f"🎹 BPM：{result.get('bpm', '未知')}",
            f"🎼 调式：{result.get('key', '未知')}",
            f"🎸 和弦走向（简略）：{result.get('chords', '未检测')}",
        ]
        if result.get("vocal_separated"):
            lines.append("✅ 人声已分离")
        return "\n".join(lines)

    def analyze_song_ai(self, song_name: str) -> str:
        """用 AI 讲解一首歌的创作思路"""
        lyric = self.kb.load_lyric(song_name)
        if not lyric:
            return f"《{song_name}》的歌词还没录入呢，你先帮我加进去吧~"

        from prompts.templates import LYRIC_ANALYSIS_PROMPT
        msg = f"帮我分析这首歌的创作思路：\n\n【歌词】\n{lyric[:1500]}"
        return self.agent.simple_chat(LYRIC_ANALYSIS_PROMPT, msg)

    # ══════════════ 模块 2b：曲风魔改 ══════════════

    def restyle_song(self, song_name: str, target_style: str) -> str:
        """保留原歌词，改编曲风格"""
        lyric = self.kb.load_lyric(song_name)
        if not lyric:
            return f"《{song_name}》的歌词还没收录~"

        prompt = (
            f"现有歌词《{song_name}》如下，请保留全部歌词内容，"
            f"但把它改编成「{target_style}」风格。\n"
            f"输出格式：\n1. 改编思路说明（编曲上做了哪些改动）\n"
            f"2. 完整歌词（标注重编的节奏/乐器提示）\n\n歌词：\n{lyric[:2000]}"
        )
        return self.agent.simple_chat(
            "你是一个擅长多种曲风的编曲制作人，能用文字描述改编方案。",
            prompt
        )

    # ══════════════ 模块 3：生成 ══════════════

    def generate_lyric(self, topic: str, style: str = "情歌") -> str:
        """生成汪苏泷风格歌词"""
        return self.lyric_gen.generate(topic, style)

    def generate_copy(self, scene: str, detail: str = "") -> str:
        """生成朋友圈/短视频文案"""
        return self.copywriter.generate(scene, detail)

    def recommend_song(self, mood: str) -> str:
        """根据心情推荐歌曲"""
        from prompts.templates import RECOMMEND_PROMPT
        return self.agent.simple_chat(RECOMMEND_PROMPT, f"我现在的心情是：{mood}，给我推荐几首合适的歌吧")

    # ══════════════ 语音 ══════════════

    def generate_voice_greeting(self, name: str, scene: str) -> str:
        """生成语音祝福"""
        # 先让 AI 写祝福词
        prompt = f"用户叫{name}，场景是{scene}。请以汪苏泷的语气，写一段30秒左右的祝福语音台词，口语化、亲切。"
        script = self.agent.simple_chat(
            "你是一个声音温暖的歌手，正在给粉丝录语音祝福。语气亲切自然，像朋友说话。",
            prompt
        )
        # 去除多余格式
        script = re.sub(r'[【】*#]', '', script)

        output_path = self.tts.speak(script, f"{name}_{scene}")
        return f"{script}\n\n🔊 语音已生成：{output_path}"

    def transcribe_audio(self, audio_path: str) -> str:
        """语音转文字（调 DeepSeek 或 whisper）"""
        try:
            import whisper
            model = whisper.load_model("tiny")  # tiny 最快，CPU 也能跑
            result = model.transcribe(audio_path, language="zh")
            return result["text"]
        except ImportError:
            return "Whisper 未安装，请运行 pip install openai-whisper"
        except Exception as e:
            return f"语音识别出错：{e}"

    # ══════════════ 音乐播放 ══════════════

    def search_music(self, keyword: str) -> list:
        """搜索歌曲"""
        return self.player.search(keyword)

    def get_player_html(self, song_id: int) -> str:
        """获取歌曲嵌入播放器 HTML"""
        return self.player.get_embed_html(song_id)

    def get_mood_music(self, mood: str) -> list:
        """按心情推荐歌曲"""
        return self.player.get_recommendations(mood)

    def get_playlist_html(self, playlist_id: str = None) -> str:
        """获取歌单嵌入播放器"""
        name = playlist_id or "汪苏泷热门50首"
        pid = self.player.DEFAULT_PLAYLISTS.get(name, "530739351")
        return self.player.get_playlist_embed(pid)
