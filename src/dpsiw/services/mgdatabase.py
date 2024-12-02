from datetime import datetime, timezone

import os
import requests
import click
from pymongo import MongoClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dpsiw.constants import constants
from dpsiw.services.settingsservice import get_settings_instance
import uuid

settings = get_settings_instance()
mg_client = None


def mogo_getConnectionStr():
    conn_str: str = ''
    if settings.is_dev:
        conn_str = settings.mongo_connection_string
    else:
        listConnectionStringUrl = settings.mongo_listconnectionstringurl
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://management.azure.com/.default"
        )
        session = requests.Session()
        token = token_provider()

        response = session.post(listConnectionStringUrl, headers={
                                "Authorization": "Bearer {}".format(token)})
        keys_dict = response.json()
        conn_str = keys_dict["connectionStrings"][0]["connectionString"]

    # Connect to Azure Cosmos DB for MongoDB
    client = MongoClient(conn_str)
    return client


def mongo_instance():
    global mg_client
    if mg_client is None:
        # mg_client = MongoClient(settings.mongo_conn_str)
        mg_client = mogo_getConnectionStr()
    return mg_client


class MongoDBService:
    def __init__(self, client: MongoClient = None, db_name: str = 'dips', collection_name: str = constants.COLLECTION_EVENTS, indexes: dict = None):
        self.client = client or mongo_instance()
        self.db_name = db_name #settings.mongo_suffix
        self.db = self.client[self.db_name]

        click.echo("Creating database")
        if db_name not in self.client.list_database_names():
            # Create a database with 400 RU throughput that can be shared across
            # the DB's collections
            self.db.command({"customAction": "CreateDatabase",
                             "offerThroughput": 600})
            click.echo(f"Created db: {self.db_name}")
        else:
            click.echo(f"Using database: {self.db_name}")

        
        self.collection_name = collection_name
        self.collection = self.db[self.collection_name]

        if collection_name not in self.db.list_collection_names():
            # Creates a unsharded collection that uses the DBs shared throughput
            self.db.command(
                {"customAction": "CreateCollection", "collection": self.collection_name}
            )
            click.echo(f"Created collection: {self.collection_name}")
        else:
            click.echo(f"Using collection: {self.collection_name}")

        self.indexes = indexes

        if self.indexes:
            self.db.command(
                {
                    "customAction": "UpdateCollection",
                    "collection": collection_name,
                    "indexes": indexes,
                }
            )

        print("exited init")

    def upsert(self, id, data: dict):
        self.collection.update_one(
            {'_id': id},
            {'$set': data},
            upsert=True
        )

    def find_id(self, id):
        return self.collection.find_one({'_id': id})

    def find_filter(self, filter):
        return self.collection.find(filter)

    def delete(self, id):
        self.collection.delete_one({'_id': id})


class EventsRepository:
    def __init__(self):
        self.mongo_service = MongoDBService(
            collection_name=constants.COLLECTION_EVENTS)

    def get_next_id(self):
        counter = self.mongo_service.collection.find_one_and_update(
            {'_id': 'event_id'},
            {'$inc': {'seq': 1}},
            upsert=True,
            return_document=True
        )
        return counter['seq']

    def insert(self, level: str, pid: str, message: str, status: str) -> None:
        """
        This method is used to log the status of a workflow
        """
        evt = {
            'level': level,
            'pid': pid,
            'message': message,
            'status': status,
            'ts': datetime.now(timezone.utc),
        }
        # Get the next auto-incremented ID
        # evt['_id'] = self.get_next_id()
        evt['_id'] = str(uuid.uuid4())
        self.mongo_service.upsert(evt['_id'], evt)


class TranscriptionsRepository:
    def __init__(self):
        indexes = [
            {"key": {"_id": 1}, "name": "_id"},
            {"key": {"updated": 2}, "name": "updated"},
        ]
        self.mongo_service = MongoDBService(
            collection_name=constants.COLLECTION_TRANSCRIPTIONS, indexes=indexes)

    def insert(self, id: str, pid: str, file_id: str, file_url: str, transcription: str, notes: str, status: str = 'processing') -> None:
        """
        This method is used to log the status of a workflow
        """
        doc = self.mongo_service.find_id(id)
        tsexists = doc and bool(doc['tstranscription'])
        noteexists = doc and bool(doc['tsnotes'])

        tstran = None
        if bool(transcription) and not tsexists:
            tstran = datetime.now(timezone.utc)
        if bool(transcription) and tsexists:
            tstran = doc['tstranscription']

        tsnote = None
        if bool(notes) and not noteexists:
            tsnote = datetime.now(timezone.utc)
        if bool(notes) and noteexists:
            tsnote = doc['tsnotes']

        evt = {
            'pid': pid,
            'file_id': file_id,
            'file_url': file_url,
            'transcription': transcription,
            'tstranscription': tstran,
            'notes': notes,
            'updatedNotes': notes,
            'tsnotes': tsnote,
            'status': status,
            'updated': datetime.now(timezone.utc)
        }

        self.mongo_service.upsert(id, evt)


# Example usage:
# db_service = MongoDBService('mongodb://localhost:27017/', 'mydatabase')
# db_service.create_collection('customers')
# db_service.upsert_customer('customers', 'customer1', {'name': 'John Doe', 'email': 'john@example.com'})
# db_service.delete_customer('customers', 'customer1')
