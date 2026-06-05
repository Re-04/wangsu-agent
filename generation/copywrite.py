"""
文案生成模块 - 朋友圈 / 短视频配文 / 乐评
"""
from prompts.templates import COPYWRITING_PROMPT


class Copywriter:
    """汪苏泷风格文案生成器"""

    SCENES = {
        "朋友圈": "朋友圈文案，感性有画面感，适合配图发圈",
        "短视频": "短视频配文，简短有力，有节奏感，10-30字",
        "乐评": "歌曲乐评，走心但有观点，100-200字",
        "表白": "表白用文案，甜而不腻，带一点羞涩感",
        "毕业": "毕业季文案，温暖的感伤，带祝福",
    }

    def __init__(self, agent):
        self.agent = agent

    def generate(self, scene: str, detail: str = "") -> str:
        """
        生成文案

        Args:
            scene: 场景（朋友圈 / 短视频 / 乐评 / 表白 / 毕业）
            detail: 更多细节描述

        Returns:
            文案文本
        """
        scene_desc = self.SCENES.get(scene, f"{scene}场景文案")

        if detail:
            user_msg = f"帮我写一段{scene_desc}。具体要求：{detail}"
        else:
            user_msg = f"帮我写一段{scene_desc}，随便发挥就好。"

        return self.agent.simple_chat(COPYWRITING_PROMPT, user_msg)

    def song_review(self, song_name: str) -> str:
        """
        写一首歌的乐评

        Args:
            song_name: 歌曲名

        Returns:
            乐评文本
        """
        from knowledge.retriever import WangKnowledgeBase
        kb = WangKnowledgeBase()
        lyric = kb.load_lyric(song_name)

        msg = f"帮我写一段关于《{song_name}》的乐评，走心风格。"
        if lyric:
            msg += f"\n\n歌词参考：\n{lyric[:1000]}"

        return self.agent.simple_chat(COPYWRITING_PROMPT, msg)
