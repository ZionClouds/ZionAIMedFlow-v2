from openai import OpenAI, AzureOpenAI
from pydantic import BaseModel


from dpsiw.messages.message import LLMOpts
from dpsiw.services.settings import Settings


class GPTMessage(BaseModel):
    """
    GPT Message
    """
    role: str
    content: str


class GPTTool:
    """
    GPTTool class to interact with OpenAI API
    """

    def __init__(self, client) -> None:
        self.client: OpenAI | AzureOpenAI | None = client

    def completion(self, opts: LLMOpts, messages: list[GPTMessage]) -> str:
        """
        Generate completion from the model
        """
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
