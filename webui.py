"""
汪苏泷 AI Agent - Gradio 网页界面
====================================
使用方式：
    python webui.py

首次运行前安装依赖：
    pip install -r requirements.txt

需要在环境变量设置 DeepSeek API Key：
    export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from agent.core import WangAgent
from agent.tools import AgentTools
from config import DEEPSEEK_API_KEY


# ────────── 全局初始化 ──────────

def init_agent():
    key = DEEPSEEK_API_KEY or os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        return None, None, "❌ 缺少 DeepSeek API Key\n\n请设置环境变量：\nDEEPSEEK_API_KEY='sk-xxx'"
    try:
        agent = WangAgent(key)
        tools = AgentTools(agent)
        return agent, tools, None
    except Exception as e:
        return None, None, f"❌ 初始化失败：{e}"


AGENT, TOOLS, ERROR_MSG = init_agent()


# ────────── 聊天功能 ──────────

def detect_intent(text: str) -> str:
    text = text.strip()
    if text.lower() in ("help", "帮助"):
        return "help"
    if text.lower() in ("intro", "介绍", "你是谁"):
        return "intro"
    if text.lower() in ("fact", "故事", "冷知识"):
        return "fact"
    if text.lower() in ("reset", "重置"):
        return "reset"
    if text.lower() in ("guess", "猜歌名"):
        return "game_guess"
    if text.lower() in ("fill", "补全歌词"):
        return "game_fill"
    if text.lower() in ("chain", "歌词接龙"):
        return "game_chain"
    if text.lower() == "stop":
        return "game_stop"
    if TOOLS and TOOLS.in_game:
        return "game_answer"
    if text.startswith("lyric") or text.startswith("歌词"):
        return "lyric"
    if text.startswith("copy") or text.startswith("文案"):
        return "copy"
    if text.startswith("review") or text.startswith("乐评"):
        return "review"
    if text.startswith("recommend") or text.startswith("推荐"):
        return "recommend"
    if text.startswith("analyze-song") or text.startswith("讲解"):
        return "analyze_song"
    return "chat"


def parse_args(text: str, cmd: str) -> str:
    for prefix in [f"{cmd} ", f"{cmd}"]:
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return ""


def respond(message, history):
    if not AGENT or not TOOLS:
        yield ERROR_MSG or "Agent 未初始化"
        return

    intent = detect_intent(message)

    if intent == "help":
        yield """**📋 可用功能**

**💬 聊天互动** — 直接说话，我用汪苏泷语气跟你聊
**🎮 歌词游戏** — `猜歌名` / `补全歌词` / `歌词接龙`
**✍️ 创作生成** — `lyric 主题` / `copy 场景` / `review 歌名` / `recommend 心情`
**🎵 歌曲分析** — `analyze-song 歌名`
**📖 冷知识** — 输入 `故事`
"""
        return
    elif intent == "intro":
        yield TOOLS.get_intro()
        return
    elif intent == "fact":
        yield TOOLS.handle_fact()
        return
    elif intent == "reset":
        AGENT.reset()
        yield "🧹 记忆已清空~"
        return
    elif intent == "game_guess":
        yield TOOLS.handle_game("guess"); return
    elif intent == "game_fill":
        yield TOOLS.handle_game("fill"); return
    elif intent == "game_chain":
        yield TOOLS.handle_game("chain"); return
    elif intent == "game_stop":
        TOOLS.in_game = False; yield "🛑 游戏结束~"; return
    elif intent == "game_answer":
        yield TOOLS.handle_game("answer", message); return
    elif intent == "lyric":
        topic = parse_args(message, "lyric") or parse_args(message, "歌词") or "即兴"
        yield f"✍️  创作中...\n\n" + TOOLS.generate_lyric(topic); return
    elif intent == "copy":
        scene = parse_args(message, "copy") or parse_args(message, "文案") or "朋友圈"
        yield "📝 " + TOOLS.generate_copy(scene); return
    elif intent == "review":
        song = parse_args(message, "review") or parse_args(message, "乐评") or ""
        if not song:
            yield "💡 示例：review 有点甜"; return
        yield "📝 " + TOOLS.copywriter.song_review(song); return
    elif intent == "recommend":
        mood = parse_args(message, "recommend") or parse_args(message, "推荐") or message
        if mood in ("recommend", "推荐"):
            yield "💡 示例：recommend 今天很开心"; return
        yield "🎵 " + TOOLS.recommend_song(mood); return
    elif intent == "analyze_song":
        song = parse_args(message, "analyze-song") or parse_args(message, "讲解") or ""
        if not song:
            yield "💡 示例：analyze-song 有点甜"; return
        yield "🎵 " + TOOLS.analyze_song_ai(song); return
    else:
        full_reply = []
        for char in TOOLS.handle_chat(message):
            full_reply.append(char)
        yield "".join(full_reply)


# ────────── 音乐播放功能 ──────────

def search_songs(keyword: str):
    """搜索歌曲，返回下拉选项列表"""
    if not keyword or not TOOLS:
        return gr.Dropdown(choices=[], value=None, label="搜索结果")
    results = TOOLS.search_music(keyword)
    if not results:
        return gr.Dropdown(choices=[], value=None, label="未找到相关歌曲")
    choices = []
    song_map = {}
    for s in results:
        label = f"{s['name']} - {s['artist']}"
        choices.append(label)
        song_map[label] = s["id"]
    return gr.Dropdown(choices=choices, value=None, label=f"找到 {len(results)} 首")


def play_song(song_label: str):
    """选择歌曲后更新播放器"""
    if not song_label or not TOOLS:
        return "<p style='color:gray'>请先搜索并选择一首歌</p>"
    results = TOOLS.search_music(song_label.split(" - ")[0])
    if results:
        song_id = results[0]["id"]
        html = TOOLS.get_player_html(song_id)
        return html
    return "<p style='color:red'>无法播放该歌曲</p>"


def quick_play(song_name: str):
    """快捷播放内置歌曲"""
    if not TOOLS:
        return "<p>请先配置 API Key</p>"
    results = TOOLS.search_music(song_name)
    if results:
        html = TOOLS.get_player_html(results[0]["id"])
        name = results[0]["name"]
        artist = results[0]["artist"]
        return f"**正在播放：{name} - {artist}**\n\n{html}"
    return "<p>暂无此歌曲</p>"


def mood_recommend(mood: str):
    """按心情推荐"""
    if not TOOLS:
        return []
    songs = TOOLS.get_mood_music(mood)
    return [f"{s['name']} - {s['artist']}" for s in songs]


# ────────── 构建页面 ──────────

def create_ui():
    _css = """
    .gradio-container { max-width: 900px !important; margin: auto !important; }
    .chat-message { font-size: 16px !important; line-height: 1.6 !important; }
    footer { display: none !important; }
    """

    with gr.Blocks(title="汪苏泷 AI Agent", css=_css) as demo:

        gr.Markdown(
            """
            # 🎵 汪苏泷 AI Agent
            > 聊天 · 听歌 · 创作 · 游戏
            """
        )

        with gr.Tabs():
            # ═══════ 标签页 1：聊天 ═══════
            with gr.TabItem("💬 聊天互动"):
                gr.ChatInterface(
                    fn=respond,
                    title="",
                    description="直接输入你想说的，或者试试下面的快捷话题",
                    examples=[
                        ["你好，介绍一下你自己"],
                        ["讲个你的幕后故事"],
                        ["猜歌名"],
                        ["lyric 毕业季"],
                        ["copy 朋友圈"],
                        ["review 有点甜"],
                        ["recommend 心情不好"],
                        ["analyze-song 万有引力"],
                    ],
                )

            # ═══════ 标签页 2：音乐播放 ═══════
            with gr.TabItem("🎶 在线听歌"):

                gr.Markdown("### 🔍 搜索歌曲（网易云音乐）")

                with gr.Row():
                    search_input = gr.Textbox(
                        label="输入歌名",
                        placeholder="例如：有点甜、万有引力...",
                        scale=4,
                    )
                    search_btn = gr.Button("🔍 搜索", variant="primary", scale=1)

                song_selector = gr.Dropdown(
                    choices=[],
                    label="搜索结果（点击选择播放）",
                    interactive=True,
                )

                player_html = gr.HTML(
                    value="<p style='color:gray; text-align:center; padding:20px;'>搜索并选择歌曲后，播放器会出现在这里</p>"
                )

                # 搜索按钮事件
                search_btn.click(
                    fn=search_songs,
                    inputs=search_input,
                    outputs=song_selector,
                )
                search_input.submit(
                    fn=search_songs,
                    inputs=search_input,
                    outputs=song_selector,
                )

                # 选择歌曲事件
                song_selector.change(
                    fn=play_song,
                    inputs=song_selector,
                    outputs=player_html,
                )

                gr.Markdown("---")
                gr.Markdown("### ⚡ 快捷播放")

                # 热门歌曲快捷按钮（分两行）
                hot_songs = [
                    "有点甜", "万有引力", "不分手的恋爱",
                    "小星星", "风度", "花千骨",
                    "年轮", "追光者", "大娱乐家",
                    "苦笑", "三国杀", "巴赫旧约",
                ]
                for i in range(0, 12, 4):
                    row_songs = hot_songs[i:i+4]
                    with gr.Row():
                        for song in row_songs:
                            btn = gr.Button(song, size="sm", min_width=80)
                            btn.click(
                                fn=quick_play,
                                inputs=[gr.State(song)],
                                outputs=player_html,
                            )

                gr.Markdown("---")
                gr.Markdown("### 🎭 按心情听歌")

                mood_input = gr.Radio(
                    choices=["😊 开心", "😢 失恋", "📖 怀旧", "🥰 甜蜜", "🌙 安静"],
                    label="你现在的心情",
                    value="😊 开心",
                )
                mood_btn = gr.Button("🎯 推荐适合的歌")
                mood_output = gr.JSON(label="推荐歌单")

                def get_mood_songs(mood_label: str):
                    mood_map = {
                        "😊 开心": "开心",
                        "😢 失恋": "失恋",
                        "📖 怀旧": "怀旧",
                        "🥰 甜蜜": "甜蜜",
                        "🌙 安静": "安静",
                    }
                    mood_key = mood_map.get(mood_label, "开心")
                    songs = TOOLS.get_mood_music(mood_key) if TOOLS else []
                    return [f"🎵 {s['name']} - {s['artist']}" for s in songs]

                mood_btn.click(
                    fn=get_mood_songs,
                    inputs=mood_input,
                    outputs=mood_output,
                )

            # ═══════ 标签页 3：关于 ═══════
            with gr.TabItem("ℹ️ 关于"):
                gr.Markdown(
                    """
                    ## 🎵 汪苏泷 AI Agent v1.0

                    **技术栈**
                    - 🤖 DeepSeek API（对话 + 创作）
                    - 🎹 Librosa（音频分析）
                    - 🔊 Edge-TTS（语音合成）
                    - 🎶 网易云音乐（在线播放）
                    - 🌐 Gradio（网页界面）

                    **功能模块**
                    - 💬 人设对话（模拟汪苏泷语气聊天）
                    - 🎮 歌词游戏（猜歌名 / 补全歌词 / 接龙）
                    - ✍️ 歌词创作（汪苏泷风格写词）
                    - 📝 文案生成（朋友圈 / 乐评）
                    - 🎵 歌曲分析（BPM / 调式 / 和弦）
                    - 🎶 在线听歌（搜索 + 播放）
                    - 🎤 语音祝福（Edge-TTS 合成）

                    **声明**
                    - 本项目为粉丝娱乐用途
                    - 所有音乐播放来自网易云音乐公开接口
                    - 歌词生成由 AI 完成，非汪苏泷本人创作

                    ---
                    Made with ❤️ by a Wang Su Long fan
                    """
                )

    return demo


# ────────── 启动 ──────────

if __name__ == "__main__":
    if ERROR_MSG:
        print(f"❌ {ERROR_MSG}")
        sys.exit(1)

    print("🎵 启动汪苏泷 AI Agent Web 界面...")
    print("   按 Ctrl+C 停止服务")

    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )
