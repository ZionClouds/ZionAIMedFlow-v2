
from time import sleep
# encoding opts: BinaryBase64EncodePolicy, BinaryBase64DecodePolicy
from azure.storage.queue import QueueClient


class AzureQueue:
    def __init__(self, client: QueueClient) -> None:
        self.queue_client = client

    @staticmethod
    def get_client(connection_string: str, queue_name: str | None = None) -> QueueClient:
        if queue_name is None:
            raise ValueError("Queue name is required")

        queue_client = QueueClient.from_connection_string(
            conn_str=connection_string, queue_name=queue_name.lower(),
            # message_encode_policy=BinaryBase64EncodePolicy(),
            # message_decode_policy=BinaryBase64DecodePolicy()
        )

        try:
            queue_client.create_queue()
        except Exception as e:
            pass
        return queue_client

    def send_message(self, message: any):
        if not self.queue_client:
            raise Exception("Queue client not initialized")
        self.queue_client.send_message(message)

    def empty_queue(self):
        if not self.queue_client:
            raise Exception("Queue client not initialized")
        properties = self.queue_client.get_queue_properties()
        count = properties.approximate_message_count
        print("Message count: " + str(count))
        self.queue_client.clear_messages()
        properties = self.queue_client.get_queue_properties()
        count = properties.approximate_message_count
        print("Message count: " + str(count))

    def count(self):
        if not self.queue_client:
            raise Exception("Queue client not initialized")
        properties = self.queue_client.get_queue_properties()
        count = properties.approximate_message_count
        print("Message count: " + str(count))
