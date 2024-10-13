from datetime import datetime
import logging

import click
from openai import AzureOpenAI, OpenAI
from dpsiw.services.llmservice import LLMService
from dpsiw.tools.gpttool import GPTMessage
from .agent import Agent
from dpsiw.messages.message import Message


class SentimentAnalysis(Agent):
    def __init__(self) -> None:
        super().__init__()
        self.message: Message = None
        self.score = -1

    def analyze(self, llm_service: LLMService) -> None:
        messages: list[GPTMessage] = [
            GPTMessage(role="system",
                       content="You are an AI sentiment analysis system. Given the user input, you should provide a sentiment score between 1 and 10 with 10 being very positive. No epilogue or prologue. Provide the score only. "),
            GPTMessage(role="user", content=self.message.metadata.content)
        ]
        resp = llm_service.completion(self.message.llmopts, messages)
        self.score = int(resp)

    def pre_validate(self) -> tuple[bool, str]:
        return (self.message is not None and self.message.metadata is not None and self.message.metadata.content is not None, "there was no message content to translate")

    def post_validate(self) -> tuple[bool, str]:
        return (self.score != -1, "")

    def save(self) -> None:
        click.echo(
            f"Original Text:\n{self.message.metadata.content}\Sentiment score: {self.score}")

    def process(self, message: Message):
        click.echo(click.style(
            f"{datetime.now().timestamp()} Processing ", fg='yellow'), nl=False)
        click.echo(click.style("Sentiment Analysis: ", fg='yellow', bold=True))
        click.echo(f"{message.metadata.content}")
        self.message = message

        (status, error_message) = self.pre_validate()
        if not status:
            logging.error(error_message)
            return

        self.log_workflow('received')

        # Workflow
        self.log_workflow('processing')

        # OpenAI client
        client = None
        if self.message.llmopts.type == 'azure':
            client = AzureOpenAI(azure_endpoint=self.message.llmopts.endpoint,
                                 api_key=self.message.llmopts.api_key, api_version=self.message.llmopts.version)
        else:
            client = OpenAI(self.message.llmopts.api_key)
        llm_service = LLMService(client)
        self.analyze(llm_service)

        (status, error_message) = self.post_validate()
        if status:
            self.save()
            self.log_workflow('completed', True)
            return True
        else:
            self.log_workflow('failure', True)
            return False
