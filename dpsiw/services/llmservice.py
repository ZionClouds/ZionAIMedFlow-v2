import logging
from openai import OpenAI, AzureOpenAI


from dpsiw.messages.message import LLMOpts
from dpsiw.tools.gpttool import GPTMessage


class LLMService:
    """
    GPTTool class to interact with OpenAI API
    """

    def __init__(self, client) -> None:
        self.client: OpenAI | AzureOpenAI | None = client

    def language_validator(self, content: str) -> str:
        """
        Filter out unwanted content
        """
        return content

    def trimmer(self, messages: list[GPTMessage], keep_system_message: bool = True, max_history: int = 4) -> list[GPTMessage]:
        if messages is None or len(messages) == 0:
            return []

        msgs = []
        if keep_system_message:
            msgs = [msg for msg in messages if messages.role == "system"]

        if len(messages) > max_history+1:
            msgs += messages[-max_history:]
        else:
            msgs += messages
        return msgs

    def completion(self, opts: LLMOpts, messages: list[GPTMessage], trim: bool = False, max_history: int = 4) -> str:
        """
        Generate completion from the model
        """
        if messages is None or len(messages) == 0 or opts is None:
            logging.error("No GPTMessage(s) or LLMOpts provided")
            return ""

        if trim:
            messages = self.trimmer(messages, max_history=max_history)

        response = self.client.chat.completions.create(
            model=opts.model,
            messages=messages,
            temperature=opts.temperature,
            max_tokens=opts.max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stream=opts.stream
        )
        # print(response)
        return response.choices[0].message.content
