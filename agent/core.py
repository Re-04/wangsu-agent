"""
Agent 核心 - 管理 DeepSeek API 调用和对话上下文
"""
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, MAX_TOKENS, TEMPERATURE
from prompts.templates import PERSONALITY_PROMPT


class WangAgent:
    """汪苏泷 AI Agent 核心"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError(
                "缺少 DeepSeek API Key！\n"
                "请设置环境变量：export DEEPSEEK_API_KEY='sk-xxx'\n"
                "或在 config.py 中直接填写"
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=DEEPSEEK_BASE_URL,
        )
        self.model = DEEPSEEK_MODEL
        self.messages = []          # 对话历史
        self.system_prompt = PERSONALITY_PROMPT

    def reset(self):
        """清空对话历史（开场白会保留）"""
        self.messages = []
        print("🧹 记忆已清空，重新开始聊天~")

    def chat(self, user_input: str, stream: bool = True) -> str:
        """
        发送消息给 DeepSeek 并获取回复
        stream=True 时实时输出，False 时一次性返回
        """
        self.messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.messages[-20:],  # 只保留最近 20 轮，避免超长上下文
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            stream=stream,
        )

        if stream:
            return self._handle_stream(response)
        else:
            return self._handle_normal(response)

    def _handle_stream(self, response) -> str:
        """处理流式输出"""
        full_content = []
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
                full_content.append(delta.content)
        print()  # 换行
        reply = "".join(full_content)
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def _handle_normal(self, response) -> str:
        """处理非流式输出"""
        reply = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def simple_chat(self, system_extra: str, user_msg: str) -> str:
        """
        单轮对话（不带历史），用于工具调用
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt + "\n\n" + system_extra},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            stream=False,
        )
        return response.choices[0].message.content
