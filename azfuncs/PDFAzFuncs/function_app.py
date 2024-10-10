from dataclasses import dataclass
import json
import logging
import uuid
import azure.functions as func
from datetime import datetime, timezone

from azurequeue import send_queue_message
from pgdatabase import BlobInfo, db_insert

app = func.FunctionApp()


@app.function_name("StorageTrigger")
@app.blob_trigger(arg_name="myblob", path="extract-in",
                  connection="StorageConnStr")
def StorageTrigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                 f"Name: {myblob.name}"
                 f"Blob Size: {myblob.length} bytes")

    blob_info = BlobInfo(str(uuid.uuid4()),
                         'extract',
                         myblob.name,
                         myblob.uri,
                         'pending',
                         datetime.now(timezone.utc).isoformat())

    # Send message to the queue
    logging.info(f"Sending message to queue: {blob_info.id}")
    send_queue_message(blob_info)

    # Write message to the database
    logging.info(f"Inserting data into the database: {blob_info.id}")
    db_insert(blob_info)

    logging.info(f"Message processed: {blob_info.id}")


@app.function_name("StorageTrigger")
@app.blob_trigger(arg_name="myblob", path="transcribe-in",
                  connection="StorageConnStr")
def StorageTrigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                 f"Name: {myblob.name}"
                 f"Blob Size: {myblob.length} bytes")

    blob_info = BlobInfo(str(uuid.uuid4()),
                         'transcribe',
                         myblob.name,
                         myblob.uri,
                         'pending',
                         datetime.now(timezone.utc).isoformat())

    # Send message to the queue
    logging.info(f"Sending message to queue: {blob_info.id}")
    send_queue_message(blob_info)

    # Write message to the database
    logging.info(f"Inserting data into the database: {blob_info.id}")
    db_insert(blob_info)

    logging.info(f"Message processed: {blob_info.id}")


@app.queue_trigger(arg_name="azqueue", queue_name="pdf-queue",
                   connection="AzureWebJobsStorage")
def queue_trigger(azqueue: func.QueueMessage):
    msg = azqueue.get_body().decode('utf-8')
    blob_info = BlobInfo.from_json(json.loads(msg))
    logging.info(f'Python Queue trigger processed a message: {blob_info}')
