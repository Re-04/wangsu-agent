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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from agent.core import WangAgent
from agent.tools import AgentTools
from config import DEEPSEEK_API_KEY


# ────────── 全局初始化 ──────────

def init_agent():
    """初始化 Agent，若 Key 缺失则提示"""
    key = DEEPSEEK_API_KEY or os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        return None, None, "❌ 缺少 DeepSeek API Key\n\n请在环境变量设置：\nDEEPSEEK_API_KEY='sk-xxx'\n\n或在 config.py 中填写"
    try:
        agent = WangAgent(key)
        tools = AgentTools(agent)
        return agent, tools, None
    except Exception as e:
        return None, None, f"❌ 初始化失败：{e}"


AGENT, TOOLS, ERROR_MSG = init_agent()


# ────────── 预处理：识别意图 ──────────

def detect_intent(text: str) -> str:
    """检测用户输入属于哪类功能"""
    text = text.strip()

    # 系统命令
    if text.lower() in ("help", "帮助"):
        return "help"
    if text.lower() in ("intro", "介绍", "你是谁"):
        return "intro"
    if text.lower() in ("fact", "故事", "冷知识"):
        return "fact"
    if text.lower() in ("reset", "重置"):
        return "reset"

    # 游戏
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

    # 创作
    if text.startswith("lyric") or text.startswith("歌词"):
        return "lyric"
    if text.startswith("copy") or text.startswith("文案"):
        return "copy"
    if text.startswith("review") or text.startswith("乐评"):
        return "review"
    if text.startswith("recommend") or text.startswith("推荐"):
        return "recommend"

    # 分析
    if text.startswith("analyze-song") or text.startswith("讲解"):
        return "analyze_song"

    # 默认走聊天
    return "chat"


# ────────── 核心处理函数 ──────────

def parse_args(text: str, cmd: str) -> str:
    """从输入中提取命令参数"""
    for prefix in [f"{cmd} ", f"{cmd}"]:
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return ""


def respond(message, history):
    """
    Gradio 聊天接口
    history: list of [user_msg, bot_msg]
    """
    if not AGENT or not TOOLS:
        yield ERROR_MSG or "Agent 未初始化"
        return

    intent = detect_intent(message)

    # ── 系统指令 ──
    if intent == "help":
        yield """**📋 可用功能**

**聊天互动**
直接说话就行，我会用汪苏泷的语气跟你聊~

**歌词游戏**
- `猜歌名` — 我给歌词片段，你猜歌名
- `补全歌词` — 挖空一句让你填
- `歌词接龙` — 我唱一句，你用最后一个字接

**创作生成**
- `lyric 主题` — 写歌词，如：lyric 毕业季
- `copy 场景` — 写文案，如：copy 朋友圈
- `review 歌名` — 写乐评，如：review 有点甜
- `recommend 心情` — 推歌，如：recommend 失恋了

**音乐分析**
- `analyze-song 歌名` — AI 讲解这首歌

**冷知识**
- `故事` — 讲个幕后趣事
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
        yield "🧹 记忆已清空，重新开始聊天~"
        return

    # ── 游戏 ──
    elif intent == "game_guess":
        yield TOOLS.handle_game("guess")
        return

    elif intent == "game_fill":
        yield TOOLS.handle_game("fill")
        return

    elif intent == "game_chain":
        yield TOOLS.handle_game("chain")
        return

    elif intent == "game_stop":
        TOOLS.in_game = False
        yield "🛑 游戏结束~"
        return

    elif intent == "game_answer":
        yield TOOLS.handle_game("answer", message)
        return

    # ── 创作 ──
    elif intent == "lyric":
        topic = parse_args(message, "lyric") or parse_args(message, "歌词")
        yield f"✍️  正在创作「{topic or '即兴'}」主题的歌词...\n\n" + TOOLS.generate_lyric(topic or "即兴")
        return

    elif intent == "copy":
        scene = parse_args(message, "copy") or parse_args(message, "文案") or "朋友圈"
        yield f"📝 正在生成{scene}文案...\n\n" + TOOLS.generate_copy(scene)
        return

    elif intent == "review":
        song = parse_args(message, "review") or parse_args(message, "乐评") or ""
        if not song:
            yield "💡 说歌名就行，比如：review 有点甜"
            return
        yield f"📝 正在写《{song}》的乐评...\n\n" + TOOLS.copywriter.song_review(song)
        return

    elif intent == "recommend":
        mood = parse_args(message, "recommend") or parse_args(message, "推荐") or message
        if mood in ("recommend", "推荐"):
            yield "💡 说说你现在的心情，比如：recommend 今天很开心"
            return
        yield f"🔍 根据「{mood}」推荐歌曲...\n\n" + TOOLS.recommend_song(mood)
        return

    # ── 音乐分析 ──
    elif intent == "analyze_song":
        song = parse_args(message, "analyze-song") or parse_args(message, "讲解") or ""
        if not song:
            yield "💡 说歌名就行，比如：analyze-song 有点甜"
            return
        yield f"🎵 正在分析《{song}》...\n\n" + TOOLS.analyze_song_ai(song)
        return

    # ── 聊天（默认） ──
    else:
        full_reply = []
        for char in TOOLS.handle_chat(message):
            full_reply.append(char)
        yield "".join(full_reply)


# ────────── 构建 Gradio 页面 ──────────

def create_ui():
    """创建 Gradio 界面"""
    _css = """
    .gradio-container { max-width: 800px !important; margin: auto !important; }
    .chat-message { font-size: 16px !important; line-height: 1.6 !important; }
    footer { display: none !important; }
    """
    with gr.Blocks(title="汪苏泷 AI Agent", css=_css) as demo:

        gr.Markdown(
            """
            # 🎵 汪苏泷 AI Agent

            > 哈喽！我是汪苏泷，跟我聊天、玩游戏、写歌词都行！
            """
        )

        # 聊天组件
        chatbot = gr.ChatInterface(
            fn=respond,
            title="",
            description="直接输入你想说的，或者试试下面的话题",
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

        # 底部信息
        gr.Markdown(
            """
            ---
            **提示**：输入 `help` 查看全部可用指令
            """
        )

    return demo


# ────────── 启动 ──────────

if __name__ == "__main__":
    if ERROR_MSG:
        print(f"❌ {ERROR_MSG}")
        print("请先设置 DeepSeek API Key 后再启动。")
        sys.exit(1)

    print("🎵 启动汪苏泷 AI Agent Web 界面...")
    print("   按 Ctrl+C 停止服务")

    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )
