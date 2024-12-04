import logging

from openai import OpenAI, AsyncOpenAI, AzureOpenAI, AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dpsiw.messages.message import LLMOpts
from dpsiw.services.settingsservice import get_settings_instance
from dpsiw.tools.gpttool import GPTMessage

settings = get_settings_instance()
aoaiclient = None
aoaiclientasync = None


def get_token_provider():
    return get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )


def get_aoai_client_instance(is_async: bool = False):
    """
    Get the Azure OpenAI client instance
    """
    global aoaiclient
    global aoaiclientasync

    if aoaiclient is None and not is_async:
        if settings.is_dev:
            aoaiclient = AzureOpenAI(azure_endpoint=settings.openai_endpoint,
                                     api_key=settings.openai_key,
                                     api_version=settings.openai_version)
        else:
            aoaiclient = AzureOpenAI(azure_endpoint=settings.openai_endpoint,
                                     azure_ad_token_provider=get_token_provider(),
                                     # api_key=settings.api_key,
                                     api_version=settings.openai_version)

    if aoaiclientasync is None and is_async:
        if settings.is_dev:
            aoaiclientasync = AsyncAzureOpenAI(azure_endpoint=settings.openai_endpoint,
                                               api_key=settings.openai_key,
                                               api_version=settings.openai_version)
        else:
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            aoaiclientasync = AsyncAzureOpenAI(azure_endpoint=settings.openai_endpoint,
                                               azure_ad_token_provider=get_token_provider(),
                                               # api_key=settings.api_key,
                                               api_version=settings.openai_version)

    if is_async:
        return aoaiclientasync
    return aoaiclient


class LLMService():
    """
    GPTTool class to interact with OpenAI API
    """

    def __init__(self, client) -> None:
        self.client: OpenAI | AzureOpenAI | AsyncAzureOpenAI | AsyncOpenAI | None = client

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

    async def completion_aio(self, opts: LLMOpts, messages: list[GPTMessage], trim: bool = False, max_history: int = 4) -> str:
        """
        Generate completion from the model
        """
        if messages is None or len(messages) == 0 or opts is None:
            logging.error("No GPTMessage(s) or LLMOpts provided")
            return ""

        if trim:
            messages = self.trimmer(messages, max_history=max_history)

        response = await self.client.chat.completions.create(
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

    async def raw_completion_aio(self, opts: LLMOpts, messages: list, trim: bool = False, max_history: int = 4) -> str:
        """
        Generate completion from the model
        """
        if messages is None or len(messages) == 0 or opts is None:
            logging.error("No GPTMessage(s) or LLMOpts provided")
            return ""

        if trim:
            messages = self.trimmer(messages, max_history=max_history)

        response = await self.client.chat.completions.create(
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
