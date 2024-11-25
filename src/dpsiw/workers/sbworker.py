import asyncio
from base64 import b64decode
from concurrent.futures import ThreadPoolExecutor
import logging
import uuid

import click
from pydantic_core import from_json
from dpsiw.agents import *
from dpsiw.messages.message import Message
from azure.servicebus.aio import ServiceBusClient
from dpsiw.services.settingsservice import get_settings_instance
from azure.identity.aio import DefaultAzureCredential

settings = get_settings_instance()


class WorkerSB:
    def __init__(self, t_id: str):
        self.t_id = t_id
        # self.client = ServiceBusClient.from_connection_string(
        #     settings.sb_connection_string)
        if settings.is_dev:
            self.client = ServiceBusClient.from_connection_string(
                settings.sb_connection_string)
        else:
            credential = DefaultAzureCredential()
            self.client = ServiceBusClient(
                settings.sb_full_ns, credential)

    async def process(self):
        while True:
            async with self.client:
                receiver = self.client.get_queue_receiver(
                    queue_name=settings.sb_queue_name)
                async with receiver:
                    received_msgs = await receiver.receive_messages(max_message_count=1, max_wait_time=60)
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

                        message = ""
                        instance: Agent = None
                        try:
                            message = Message.model_validate(
                                from_json(content, allow_partial=True))
                            # NOTE: Dynamically instantiate the agent based on the message type
                            instance: Agent = eval(message.type)()
                            click.echo(f"Processing instance: {instance}")
                            if instance:
                                await instance.process(message)
                        # except CompletedException as e:
                        #     logging.error(
                        #         f"Completed message with exception: {e.message}")
                        #     await receiver.complete_message(msg)
                        # except AbandonedException as e:
                        #     logging.error(
                        #         f"Abandoning the message {e.message}")
                        #     await receiver.abandon_message(msg)
                        # except DeadLetteredException as e:
                        #     logging.error(
                        #         f"Deadlettering the message {e.message}")
                        #     await receiver.dead_letter_message(msg)
                        except Exception as e:
                            logging.error(f"Deadlettering with exception: {e}")
                            try:
                                await receiver.dead_letter_message(msg)
                                continue
                            except Exception as e:
                                logging.error(
                                    f"Error deadlettering message: {e}")
                                continue

                        try:
                            if msg:
                                await receiver.complete_message(msg)
                        except Exception as e:
                            logging.error(f"Error completing message: {e}")

    @staticmethod
    async def start(instances: int = 1, endless: bool = False):
        click.echo(click.style(
            f"Starting {instances} worker instances", fg="cyan"))

        # tasks = []
        # for _ in range(instances):
        #     id = str(uuid.uuid4())[:6]
        #     t = asyncio.create_task(WorkerSB(id).process())
        #     print(f"Thread ID: {id} started")
        #     tasks.append(t)

        # await asyncio.wait(tasks)

        # Create multiple tasks
        # loop = asyncio.get_event_loop()
        # with ThreadPoolExecutor(max_workers=5) as executor:
        #     tasks = []
        #     for i in range(5):
        #         # Use loop.run_in_executor to run the blocking worker in a separate thread
        #         id = str(uuid.uuid4())[:6]
        #         task = asyncio.create_task(loop.run_in_executor(
        #             executor, WorkerSB(id).process))
        #         tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*[await asyncio.to_thread(WorkerSB(str(uuid.uuid4())[:6]).process) for _ in range(instances)])
