import os
import uuid
import logging

import azure.functions as func
from mgdatabase import EventsRepository
from models import *
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential


MSG_TYPE_MEDICAL_NOTES = "MedicalNotesAgent"
BLOB_PATH = "medical-notes-in"

load_dotenv()
app = func.FunctionApp()


async def send_queue_message(correlation_id: str, payload: str):
    queue_name = os.getenv("SB_QUEUE")
    credential = DefaultAzureCredential()
    client = ServiceBusClient(os.getenv("SB_ENDPOINT"), credential)
    # client = ServiceBusClient.from_connection_string(
    #     os.getenv("SB_CONNECTION_STRING"))
    async with client:
        sender = client.get_queue_sender(queue_name=queue_name)
        # Create a Service Bus message and send it to the queue
        message = ServiceBusMessage(payload, correlation_id=correlation_id)
        await sender.send_messages(message)
        logging.info(f"Message sent to queue: {queue_name}")


@app.function_name("StorageTrigger")
@app.blob_trigger(arg_name="myblob", path=BLOB_PATH,
                  connection="AzureWebJobsStorage")
async def StorageTrigger(myblob: func.InputStream):

    logging.info(f"Python blob trigger function processed blob"
                 f"Name: {myblob.name}"
                 f"Blob Size: {myblob.length} bytes")

    # Prepare the message data
    correlation_id = str(uuid.uuid4())
    file_name = os.path.basename(myblob.name)
    (file, _) = os.path.splitext(file_name)
    file_id = file.split("-")[1]

    if not bool(file_id):
        logging.error(
            f"{myblob.name} could not be parsed. Expected format: PROVIDER-FILE_ID.wav")
        return

    # Build the message
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
    await send_queue_message(correlation_id, message.model_dump_json())

    # Log the event to MongoDB
    repository = EventsRepository()
    repository.event(
        'INFO', correlation_id, f'Blob URI: {myblob.uri}', 'Blob uploaded and message sent to queue')

    # Log the event to the console
    logging.info(f"Prossed event for: {myblob.uri}")
