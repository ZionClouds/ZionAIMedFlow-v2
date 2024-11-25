import logging
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.servicebus.management import ServiceBusAdministrationClient
from azure.identity.aio import DefaultAzureCredential
import click

from dpsiw.services.settingsservice import get_settings_instance

settings = get_settings_instance()


class AzureSB:
    def __init__(self):
        self.queue_name = settings.sb_queue_name
        if settings.is_dev:
            self.client = ServiceBusClient.from_connection_string(
                settings.sb_connection_string)
            self.adminclient = ServiceBusAdministrationClient.from_connection_string(
                settings.sb_connection_string)
        else:
            credential = DefaultAzureCredential()
            self.client = ServiceBusClient(settings.sb_mi_ns, credential)
            self.adminclient = ServiceBusAdministrationClient(
                settings.sb_mi_ns, credential)
        self.sender = self.client.get_queue_sender(
            queue_name=settings.sb_queue_name)
        self.receiver = self.client.get_queue_receiver(
            queue_name=settings.sb_queue_name)

    async def send_message(self, id: str, payload: str):
        async with self.client:
            sender = self.client.get_queue_sender(queue_name=self.queue_name)
            # Create a Service Bus message and send it to the queue
            message = ServiceBusMessage(payload, correlation_id=id)
            await sender.send_messages(message)
            logging.info(f"Message sent to queue: {self.queue_name}")

    def process_messages(self, callback):
        while True:
            received_msgs = self.receiver.receive_messages()
            with self.receiver:
                for msg in received_msgs:
                    callback(msg)
                    logging.info(f"Received: {msg}")
                    msg.complete()
                    logging.info(f"Completed: {msg}")

    async def purge(self):
        ctx = 0
        while True:
            async with self.client:
                receiver = self.client.get_queue_receiver(
                    queue_name=self.queue_name)
                async with receiver:
                    received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
                    if not received_msgs:
                        break
                    for msg in received_msgs:
                        await receiver.complete_message(msg)
                        ctx += 1
        click.echo(f"Purged {ctx} messages from queue: {self.queue_name}")

    def count_messages(self):
        queue_runtime_properties = self.adminclient.get_queue_runtime_properties(
            self.queue_name)
        click.echo(f"Queue Name: {queue_runtime_properties.name}")
        click.echo(f"Queue Runtime Properties:")
        click.echo(f"Updated at: { queue_runtime_properties.updated_at_utc}")
        click.echo(f"Size in Bytes: {queue_runtime_properties.size_in_bytes}")
        click.echo(
            f"Message Count: {queue_runtime_properties.total_message_count}")
        click.echo(
            f"Active Message Count: {queue_runtime_properties.active_message_count}")
        click.echo(
            f"Scheduled Message Count: {queue_runtime_properties.scheduled_message_count}")
        click.echo(
            f"Dead-letter Message Count: {queue_runtime_properties.dead_letter_message_count}")


azuresb_instance = None


def get_azuresb_instance():
    global azuresb_instance
    if azuresb_instance is None:
        azuresb_instance = AzureSB()
    return azuresb_instance
