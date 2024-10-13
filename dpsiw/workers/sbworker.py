import asyncio
from base64 import b64decode
import logging
# import threading
from time import sleep
import uuid

import click
from pydantic_core import from_json

from dpsiw.agents.agent import Agent
from dpsiw.constants import constants
from dpsiw.messages.message import Message
from dpsiw.agents import *
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient


from dpsiw.services.azureservicebus import AzureSB, get_azuresb_instance

settings = get_settings_instance()


# def lock_failure_callback(msg):
#     """
#     Callback function to handle lock failures
#     """
#     logging.error(f"Lock failure for message: {msg}")
#     msg.dead_letter()


# class SBWorker:
#     def __init__(self, t_id: str):
#         self.t_id = t_id
#         self.servicebus_client = ServiceBusClient.from_connection_string(
#             SB_CONNECTION_STRING)

#     async def work(self):
#         while True:
#             async with self.servicebus_client:
#                 receiver = self.servicebus_client.get_queue_receiver(
#                     queue_name=SB_QUEUE)
#                 async with receiver:
#                     received_msgs = await receiver.receive_messages(max_message_count=1, max_wait_time=5)
#                     if len(received_msgs) == 0:
#                         await asyncio.sleep(5)
#                     for msg in received_msgs:
#                         print(self.t_id, ":", str(msg))
#                         await receiver.complete_message(msg)


# # async def consume(instances):
# #     tasks = []
# #     for i in range(instances):
# #         id = str(uuid.uuid4())[:6]
# #         t = asyncio.create_task(SBWorker(id).work())
# #         print(f"Thread with {id} started")
# #         tasks.append(t)
# #     for t in tasks:
# #         await t


# class WorkerSB:
#     """
#     Worker class to listen to messages on a queue and process them
#     """

#     def __init__(self, action: any = None):
#         self.azuresb: AzureSB = get_azuresb_instance()
#         self.action = None  # deletage

#     def process(self, endless: bool = True):
#         """
#         Process messages from the queue
#         """
#         if not self.azuresb:
#             raise Exception("Azure Service Bus instance not initialized")
#         click.echo(
#             f"Service Bus listening to messages on: {self.azuresb.queue_name}")
#         while True:
#             messages = self.azuresb.receiver.receive_messages(
#                 max_message_count=1,
#                 max_wait_time=60)
#             for msg in messages:
#                 self.azuresb.auto_lock.register(self.azuresb.receiver, msg,
#                                                 max_lock_renewal_duration=300)
#                 content = ""
#                 # NOTE: messages put on Azure functions are base64 encoded
#                 # TODO: Maybe consider changing all messages to base64
#                 try:
#                     content = b64decode(msg).decode('utf-8')
#                 except Exception as e:
#                     content = str(msg)

#                 message = Message.model_validate(
#                     from_json(content, allow_partial=True))
#                 try:
#                     # NOTE: Dynamically instantiate the agent based on the message type
#                     instance: Agent = eval(message.type)()
#                     click.echo(f"Instance: {instance}")
#                     if instance:
#                         instance.process(message)
#                 except Exception as e:
#                     logging.ERROR("unable to instantiate type", e)
#                     self.azuresb.receiver.dead_letter_message(msg)

#                 self.azuresb.receiver.complete_message(msg)
#             if not endless:
#                 break
#             sleep(1)

#     @staticmethod
#     async def start(instances: int = 1, endless: bool = False):
#         click.echo(click.style(
#             f"Starting {instances} worker instances", fg="cyan"))

#         tasks = []
#         for i in range(instances):
#             id = str(uuid.uuid4())[:6]
#             t = asyncio.create_task(WorkerSB(id).process())
#             print(f"Thread with {id} started")
#             tasks.append(t)
#         for t in tasks:
#             await t

settings = get_settings_instance()


class AbandonedException(Exception):
    def __init__(self, message):
        super().__init__(message)


class DeadLetteredException(Exception):
    def __init__(self, message):
        super().__init__(message)


class WorkerSB:
    def __init__(self, t_id: str):
        self.t_id = t_id
        self.client = ServiceBusClient.from_connection_string(
            settings.sb_connection_string)

    async def process(self):
        while True:
            async with self.client:
                receiver = self.client.get_queue_receiver(
                    queue_name=settings.sb_queue_name)
                async with receiver:
                    received_msgs = await receiver.receive_messages(max_message_count=1, max_wait_time=5)
                    if not received_msgs:
                        await asyncio.sleep(2.5)
                        continue
                    for msg in received_msgs:
                        content = ""
                        # NOTE: messages put on Azure functions are base64 encoded
                        # TODO: Maybe consider changing all messages to base64
                        try:
                            content = b64decode(msg).decode('utf-8')
                        except Exception as e:
                            content = str(msg)

                        logging.info(f"Processing: {content}")

                        message = Message.model_validate(
                            from_json(content, allow_partial=True))
                        try:
                            # NOTE: Dynamically instantiate the agent based on the message type
                            instance: Agent = eval(message.type)()
                            click.echo(f"Processing instance: {instance}")
                            if instance:
                                instance.process(message)
                        except Exception as e:
                            logging.ERROR("unable to instantiate type", e)
                            receiver.dead_letter_message(msg)

                        receiver.complete_message(msg)

    @staticmethod
    async def start(instances: int = 1, endless: bool = False):
        click.echo(click.style(
            f"Starting {instances} worker instances", fg="cyan"))

        tasks = []
        for _ in range(instances):
            id = str(uuid.uuid4())[:6]
            t = asyncio.create_task(WorkerSB(id).process())
            print(f"Thread ID: {id} started")
            tasks.append(t)
        for t in tasks:
            await t
