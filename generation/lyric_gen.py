"""
歌词生成模块 - 调用 DeepSeek 生成汪苏泷风格歌词
"""
from prompts.templates import LYRIC_GENERATION_PROMPT


class LyricGenerator:
    """汪苏泷风格歌词生成器"""

    def __init__(self, agent):
        self.agent = agent

    def generate(self, topic: str, style: str = "情歌") -> str:
        """
        生成歌词

        Args:
            topic: 歌词主题
            style: 风格（情歌 / 中国风 / 甜蜜 / 伤感 / 励志）

        Returns:
            歌词文本
        """
        user_msg = (
            f"帮我写一首{style}风格的歌词，主题是：{topic}。\n"
            f"请严格按照汪苏泷的风格来写，押韵工整，结构完整。"
        )

        return self.agent.simple_chat(LYRIC_GENERATION_PROMPT, user_msg)

    def generate_with_theme(self, keywords: list[str]) -> str:
        """
        根据关键词写歌词

        Args:
            keywords: 关键词列表，如 ["毕业", "夏天", "再见"]

        Returns:
            歌词文本
        """
        user_msg = (
            f"请用以下关键词写一首歌：{'、'.join(keywords)}\n"
            f"汪苏泷风格，完整歌词。"
        )
        return self.agent.simple_chat(LYRIC_GENERATION_PROMPT, user_msg)
