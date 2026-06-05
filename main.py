"""
汪苏泷 AI Agent - CLI 入口
============================
使用方式：
    python main.py              # 普通交互模式
    python main.py --once "你好" # 单次问答

首次运行前：
    1. 设置 DeepSeek API Key
       export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
    2. 安装依赖
       pip install -r requirements.txt
"""
import sys
import os

# 确保能导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import WangAgent
from agent.tools import AgentTools
from config import DEEPSEEK_API_KEY


def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════╗
    ║     🎵 汪苏泷 AI Agent v1.0         ║
    ║     输入你想聊的 / 想玩的 / 想听的   ║
    ║     输入 help 查看所有指令           ║
    ║     输入 exit 退出                   ║
    ╚══════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """打印帮助信息"""
    help_text = """
📋 可用指令：

【闲聊互动】
  help                显示本帮助
  intro               让 AI 介绍自己
  fact                讲一个汪苏泷的幕后故事

【歌词游戏】
  guess               猜歌名
  fill                补全歌词
  chain               歌词接龙
  stop                结束当前游戏

【创作生成】
  lyric <主题>        写一首歌词，如：lyric 毕业季
  copy <场景>         写文案，如：copy 朋友圈
  review <歌名>       写乐评，如：review 有点甜
  recommend <心情>    推荐歌曲，如：recommend 失恋

【音乐分析（需音频文件路径）】
  analyze <路径>      分析音频文件
  analyze-song <歌名> AI 讲解这首歌

【语音】
  voice <名字> <场景> 生成语音祝福
                      如：voice 小红 表白

【系统】
  reset               清空对话历史
  exit                退出程序

【自由对话】
  直接输入你想说的话，AI 会以汪苏泷身份跟你聊天
    """
    print(help_text)


def main():
    # 检查 API Key
    if not DEEPSEEK_API_KEY:
        print("❌ 未设置 DeepSeek API Key！")
        key = input("请输入你的 DeepSeek API Key（输入后直接回车确认）: ").strip()
        if key:
            os.environ["DEEPSEEK_API_KEY"] = key
        else:
            print("请设置环境变量：export DEEPSEEK_API_KEY='sk-xxx'")
            sys.exit(1)

    # 初始化
    agent = WangAgent(os.environ.get("DEEPSEEK_API_KEY"))
    tools = AgentTools(agent)
    print_banner()
    print(tools.get_intro())

    while True:
        try:
            user_input = input("\n🎤 你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 下次再聊~")
            break

        if not user_input:
            continue

        # 处理系统命令
        cmd = user_input.split()[0].lower()

        if cmd in ("exit", "quit", "q"):
            print("👋 拜拜！记得多听歌~")
            break

        elif cmd == "help":
            print_help()
            continue

        elif cmd == "reset":
            agent.reset()
            continue

        elif cmd == "intro":
            print("\n🤖 ", end="")
            print(tools.get_intro())
            continue

        elif cmd == "fact":
            print("\n🤖 ", end="")
            print(tools.handle_fact())
            continue

        # === 游戏指令 ===
        elif cmd in ("guess", "fill", "chain"):
            print("\n🎮 ", end="")
            print(tools.handle_game(cmd))
            continue

        elif cmd == "stop" and tools.in_game:
            tools.in_game = False
            print("🛑 游戏结束~")
            continue

        # === 游戏答案提交 ===
        elif tools.in_game:
            print("\n🤖 ", end="")
            print(tools.handle_game("answer", user_input))
            continue

        # === 创作生成指令 ===
        elif cmd == "lyric":
            topic = user_input[5:].strip()
            if not topic:
                print("💡 示例：lyric 毕业季的遗憾")
                continue
            print(f"\n✍️  正在创作《{topic}》风格的歌词...\n")
            print(tools.generate_lyric(topic))
            continue

        elif cmd == "copy":
            scene = user_input[4:].strip() or "朋友圈"
            print(f"\n📝 正在生成{scene}文案...\n")
            print(tools.generate_copy(scene))
            continue

        elif cmd == "review":
            song = user_input[6:].strip()
            if not song:
                print("💡 示例：review 有点甜")
                continue
            print(f"\n📝 正在写《{song}》的乐评...\n")
            print(tools.copywriter.song_review(song))
            continue

        elif cmd == "recommend":
            mood = user_input[9:].strip()
            if not mood:
                print("💡 示例：recommend 失恋了很难过")
                continue
            print(f"\n🔍 根据「{mood}」推荐歌曲...\n")
            print(tools.recommend_song(mood))
            continue

        # === 音乐分析指令 ===
        elif cmd == "analyze":
            path = user_input[7:].strip()
            if not path:
                print("💡 示例：analyze /path/to/song.mp3")
                continue
            print(f"\n🎵 正在分析音频文件...\n")
            print(tools.analyze_audio(path))
            continue

        elif cmd == "analyze-song":
            song = user_input[12:].strip()
            if not song:
                print("💡 示例：analyze-song 有点甜")
                continue
            print(f"\n🎵 正在分析《{song}》...\n")
            print(tools.analyze_song_ai(song))
            continue

        # === 语音指令 ===
        elif cmd == "voice":
            parts = user_input[5:].strip().split(maxsplit=1)
            if len(parts) < 2:
                print("💡 示例：voice 小红 表白")
                continue
            name, scene = parts
            print(f"\n🔊 正在生成给{name}的{scene}祝福语音...\n")
            print(tools.generate_voice_greeting(name, scene))
            continue

        # === 自由对话（默认） ===
        else:
            print("\n🤖 ", end="")
            tools.handle_chat(user_input)


if __name__ == "__main__":
    main()
