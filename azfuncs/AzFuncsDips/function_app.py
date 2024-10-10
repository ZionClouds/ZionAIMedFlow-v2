import os
import uuid
import azure.functions as func
from mgdatabase import EventsRepository
from models import *

import logging

from dotenv import load_dotenv
from azure.storage.queue import QueueClient,  BinaryBase64EncodePolicy

MSG_TYPE_MEDICAL_NOTES = "MedicalNotesAgent"
BLOB_PATH = "medical-notes-in"

load_dotenv()
app = func.FunctionApp()


def send_queue_message(json_data: str):
    queue_client = QueueClient.from_connection_string(
        conn_str=os.getenv('STORAGE_CONN_STR'),
        queue_name="dips-messages",
        message_encode_policy=BinaryBase64EncodePolicy()

    )
    message_content = json_data.encode('ascii')
    queue_client.send_message(message_content)


@app.function_name("StorageTrigger")
@app.blob_trigger(arg_name="myblob", path=BLOB_PATH,
                  connection="AzureWebJobsStorage")
def StorageTrigger(myblob: func.InputStream):

    logging.info(f"Python blob trigger function processed blob"
                 f"Name: {myblob.name}"
                 f"Blob Size: {myblob.length} bytes")

    correlation_id = str(uuid.uuid4())
    file_name = os.path.basename(myblob.name)
    (file, _) = os.path.splitext(file_name)
    file_id = file.split("-")[1]
    # logging.info(
    #     f"Extracted file name with extension: {file_name}")

    if not bool(file_id):
        logging.error(
            f"{myblob.name} could not be parsed. Expected format: PROVIDER-FILE_ID.wav")

    message = Message(id=correlation_id,
                      type=MSG_TYPE_MEDICAL_NOTES,
                      metadata=MedicalNotesMD(
                          file_url=myblob.uri,
                          blob_name=myblob.name,
                          file_id=file_id)
                      )

    # Send message to the queue
    logging.info(
        f"Sending base64 message to queue: medical-notes-in with ID: {correlation_id}")
    send_queue_message(message.model_dump_json())

    repository = EventsRepository()
    repository.event(
        'INFO', correlation_id, f'Blob URI: {myblob.uri}', 'Blob uploaded and message sent to queue')

    # logging.info(
    #     f"Prossed event for: {myblob.uri}")
