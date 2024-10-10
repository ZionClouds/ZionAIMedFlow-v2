from datetime import datetime
import logging
import click
from openai import AzureOpenAI, OpenAI

from dpsiw.tools.gpttool import GPTMessage, GPTTool
from .agent import Agent
from dpsiw.messages.message import Message


class ProductGeneration(Agent):
    def __init__(self) -> None:
        super().__init__()
        self.client = None
        self.product_description = ""

    def generate(self, tool: GPTTool) -> None:
        messages: list[GPTMessage] = [
            GPTMessage(role="system",
                       content=self.message.llmopts.system_message),
            GPTMessage(role="user", content=self.message.metadata.content)
        ]
        self.product_description = tool.completion(
            self.message.llmopts, messages)

    def pre_validate(self) -> tuple[bool, str]:
        return (self.message is not None and self.message.metadata is not None and self.message.metadata.content is not None, "there was no message content to generate a product description")

    def post_validate(self) -> tuple[bool, str]:
        return (self.product_description.strip() != "", "no product description generated")

    def save(self) -> None:
        click.echo(
            f"Product Description:\n{self.message.metadata.content}\n{self.product_description}")

    def process(self, message: Message) -> None:
        click.echo(click.style(
            f"{datetime.now().timestamp()} Processing ", fg='yellow'), nl=False)
        click.echo(click.style("Product Generation: ", fg='yellow', bold=True))
        self.message = message

        (status, error_message) = self.pre_validate()
        if not status:
            logging.error(error_message)
            return

        self.log_workflow('received')

        click.echo(f"{self.message.metadata.content}")

        self.client = None
        if self.message.llmopts.type == 'azure':
            self.client = AzureOpenAI(azure_endpoint=self.message.llmopts.endpoint,
                                      api_key=self.message.llmopts.api_key, api_version=self.message.llmopts.version)
        else:
            self.client = OpenAI(self.message.llmopts.api_key)
        gpt_tool = GPTTool(self.client)

        self.log_workflow('processing')

        self.generate(gpt_tool)

        (status, error_message) = self.post_validate()
        if status:
            self.save()
            self.log_workflow('completed', completed=True)
        else:
            self.log_workflow('failure', completed=True)
