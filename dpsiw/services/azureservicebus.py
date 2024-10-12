import logging
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.management import ServiceBusAdministrationClient
import click

from dpsiw.services.settings import get_settings_instance


class AzureSB:
    def __init__(self, queue_name: str, conn_str: str):
        self.queue_name = queue_name
        self.client = ServiceBusClient.from_connection_string(conn_str)
        self.adminclient = ServiceBusAdministrationClient.from_connection_string(
            conn_str=conn_str)
        self.sender = self.client.get_queue_sender(queue_name=queue_name)
        self.receiver = self.client.get_queue_receiver(queue_name=queue_name)

    def send_message(self, id: str, payload: str):
        # Create a Service Bus message and send it to the queue
        message = ServiceBusMessage(payload, correlation_id=id)
        self.sender.send_messages(message)
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

    def purge(self):
        with self.client:
            receiver = self.client.get_queue_receiver(
                queue_name=self.queue_name)
            with receiver:
                # Receive messages in a loop until the queue is empty
                while True:
                    messages = receiver.receive_messages(
                        max_message_count=10, max_wait_time=5)
                    if not messages:
                        break
                    for message in messages:
                        print(f"Purging message: {message}")
                        receiver.complete_message(message)

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


settings = get_settings_instance()
azuresb_instance = None


def get_azuresb_instance():
    global azuresb_instance
    if azuresb_instance is None:
        azuresb_instance = AzureSB(
            settings.sb_queue_name, settings.sb_connection_string)
    return azuresb_instance
