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
from dpsiw.services.servicecontainer import get_service_container_instance
from azure.storage.queue import QueueClient

service_container = get_service_container_instance()


class Worker:
    """
    Worker class to listen to messages on a queue and process them
    """

    def __init__(self, queue_client: QueueClient = None, action: any = None):
        self.queue_client = queue_client
        self.action = None  # deletage

    def process(self, endless: bool = True):
        """
        Process messages from the queue
        """
        if not self.queue_client:
            raise Exception("Queue client not initialized")
        # properties = self.queue_client.get_queue_properties()
        # count = properties.approximate_message_count
        # print("Message count: " + str(count))
        click.echo(f"Listening to messages on: {self.queue_client.queue_name}")
        while True:
            messages = self.queue_client.receive_messages(messages_per_page=5)
            for msg in messages:
                content = ""
                # NOTE: messages put on Azure functions are base64 encoded
                # TODO: Maybe consider changing all messages to base64
                try:
                    content = b64decode(msg.content).decode('utf-8')
                except Exception as e:
                    content = str(msg.content)

                message = Message.model_validate(
                    from_json(content, allow_partial=True))
                try:
                    # INFO: Dynamically instantiate the agent based on the message type
                    instance: Agent = eval(message.type)()
                    click.echo(f"Instance: {instance}")
                    if instance:
                        instance.process(message)
                except Exception as e:
                    logging.ERROR("unable to instantiate type", e)
                self.queue_client.delete_message(msg)
            if not endless:
                break
            sleep(1)

    def start(self, instances: int = 1, endless: bool = False):
        click.echo(click.style(
            f"Starting {instances} worker instances", fg="cyan"))
        threads = list()
        worker = Worker(service_container.get(
            constants.SERVICE_MESSAGES_QUEUE).queue_client)
        for _ in range(instances):
            t = threading.Thread(target=worker.process, args=(endless,))
            threads.append(t)
            t.start()
            # azurequeue.consumer(queue_client)

        for index, thread in enumerate(threads):
            thread.join()
