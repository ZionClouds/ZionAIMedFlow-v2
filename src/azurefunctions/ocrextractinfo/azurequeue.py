from datetime import datetime
import json
import logging
import os
import uuid
from azure.storage.queue import QueueClient, QueueMessage, BinaryBase64EncodePolicy
from dotenv import load_dotenv

from src.azurefunctions.ocrextractinfo.pgdatabase import BlobInfo


def send_queue_message(blob_info: BlobInfo):
    env = os.getenv('StorageConnStr')

    queue_client = QueueClient.from_connection_string(
        conn_str=env,
        queue_name="pdf-queue",
        message_encode_policy=BinaryBase64EncodePolicy()

    )

    # Create a message with the blob information
    message_content = json.dumps(blob_info.to_json()).encode('ascii')
    # get an array of bytes

    queue_client.send_message(message_content)
