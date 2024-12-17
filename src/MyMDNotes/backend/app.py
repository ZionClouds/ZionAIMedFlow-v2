from datetime import datetime, timezone
import logging
import uuid
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import FastAPI, File, HTTPException, UploadFile
from azure.storage.blob import BlobServiceClient
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential

from settings import Settings, get_settings_instance
from mgdatabase import MongoDBService
from constants import *

AZURE_CONTAINER_NAME = 'medical-notes-in'
settings: Settings = get_settings_instance()

def get_blob_service_client() -> BlobServiceClient:
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(settings.blob_connection_string, credential=credential)
    print(settings.blob_connection_string)
    return blob_service_client

blob_service_client = get_blob_service_client()

# blob_service_client = BlobServiceClient.from_connection_string(
#     settings.blob_connection_string)

mongo_service = MongoDBService(
    collection_name=constants.COLLECTION_TRANSCRIPTIONS)



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_file_name_and_extension(filename: str):
    name, extension = os.path.splitext(filename)
    return name, extension


class MDNotes(BaseModel):
    pid: str
    id: str
    status: str
    file_id: str
    file_url: str
    transcription: str
    notes: str
    updatedNotes: str
    updated: datetime


@app.get("/status")
def status():
    return {"status": 1}


@app.delete("/truncate")
def truncate_collect():
    """
    Truncate all the collection
    NOTE: This is a dangerous operation and should be removed in production
    """
    try:
        mongo_service.collection.delete_many({})
        return {"status": "collection truncated"}
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Something went wrong truncating the collection")


@app.get("/notes/{id}", response_model=list[MDNotes])
def get_notes(id: str):
    list = []
    try:
        cursor = mongo_service.collection.find(
            {"pid": id}).sort('updated', -1)

        if cursor:
            # list = [doc for doc in cursor]
            for doc in cursor:
                print(doc)
                list.append(MDNotes(
                    pid=doc['pid'],
                    id=doc['_id'],
                    status=doc['status'],
                    file_id=doc['file_id'],
                    file_url=doc['file_url'],
                    transcription=doc['transcription'],
                    notes=doc['notes'],
                    updatedNotes=doc['updatedNotes'],
                    updated=doc['updated']
                ))
                # TODO: Add the updated to MongoDB Index, to make it work we did it manually
            # if len(list) == 0:
            #     raise HTTPException(status_code=404, detail="No notes found")
            return list
        else:
            raise HTTPException(
                status_code=404, detail="Unable to fetch notes")
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Something went wrong fetching the notes")


@app.post("/notes")
def update_notes(request: MDNotes):
    if not bool(request.updatedNotes) or not bool(request.id):
        raise HTTPException(
            status_code=400, detail="The correlation ID or notes cannot be empty for update")

    try:
        data = {
            'updatedNotes': request.updatedNotes,
            'updated': datetime.now(timezone.utc)
        }

        mongo_service.collection.update_one(
            {'_id': request.id},
            {'$set': data},
            upsert=True
        )

        return {"status": f"notes updated: {id}"}
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Something went wrong updating the notes")


@app.post("/upload/{id}")
async def upload_file(id: str, file: UploadFile = File(...)):
    uid = str(uuid.uuid4()).replace("-", "")[:10]
    _, extension = os.path.splitext(file.filename)
    blob_name = f"{id}-{uid}{extension}"
    # Create a blob client with the new name
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_CONTAINER_NAME, blob=blob_name)

    # Open the file and write it to the buffer
    with open("./"+file.filename, "wb") as buffer:
        buffer.write(await file.read())

    # Open the file and upload it to the blob
    with open("./"+file.filename, "rb") as data:
        blob_client.upload_blob(data)

    # Delete the file from the server
    os.remove("./"+file.filename)

    # Return the blob name
    return {"filename": blob_name}

# Static files setup (unchanged from your original code)
local_folder = os.path.dirname(os.path.abspath(__file__))
static_foler = os.path.join(local_folder, 'static')
print(static_foler)
app.mount("/", StaticFiles(directory=static_foler,
                           html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
