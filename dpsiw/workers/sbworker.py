from base64 import b64decode
import logging
import threading
from time import sleep

import click
from pydantic_core import from_json

from dpsiw.agents.agent import Agent
from dpsiw.constants import constants
from dpsiw.messages.message import Message
from dpsiw.agents import *


from dpsiw.services.azureservicebus import AzureSB, get_azuresb_instance

settings = get_settings_instance()


class WorkerSB:
    """
    Worker class to listen to messages on a queue and process them
    """

    def __init__(self, action: any = None):
        self.azuresb: AzureSB = get_azuresb_instance()
        self.action = None  # deletage

    def process(self, endless: bool = True):
        """
        Process messages from the queue
        """
        if not self.azuresb:
            raise Exception("Azure Service Bus instance not initialized")
        click.echo(
            f"Service Bus listening to messages on: {self.azuresb.queue_name}")
        while True:
            messages = self.azuresb.receiver.receive_messages(
                max_message_count=1,
                max_wait_time=60)
            for msg in messages:
                content = ""
                # NOTE: messages put on Azure functions are base64 encoded
                # TODO: Maybe consider changing all messages to base64
                try:
                    content = b64decode(msg).decode('utf-8')
                except Exception as e:
                    content = str(msg)

                message = Message.model_validate(
                    from_json(content, allow_partial=True))
                try:
                    # NOTE: Dynamically instantiate the agent based on the message type
                    instance: Agent = eval(message.type)()
                    click.echo(f"Instance: {instance}")
                    if instance:
                        instance.process(message)
                except Exception as e:
                    logging.ERROR("unable to instantiate type", e)
                self.azuresb.receiver.complete_message(msg)
            if not endless:
                break
            sleep(1)

    def start(self, instances: int = 1, endless: bool = False):
        click.echo(click.style(
            f"Starting {instances} worker instances", fg="cyan"))
        threads = list()
        worker = WorkerSB()
        for _ in range(instances):
            t = threading.Thread(target=worker.process, args=(endless,))
            threads.append(t)
            t.start()
            # azurequeue.consumer(queue_client)

        for _, thread in enumerate(threads):
            thread.join()
