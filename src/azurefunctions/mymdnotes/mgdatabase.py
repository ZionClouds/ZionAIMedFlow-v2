import os
from datetime import datetime, timezone

from pymongo import MongoClient
from dotenv import load_dotenv

mg_client = None


def mongo_instance():
    global mg_client
    if mg_client is None:
        load_dotenv()
        mg_client = MongoClient(os.getenv('MONGO_DB'))
    return mg_client


class MongoDBService:
    def __init__(self, client: MongoClient = None, db_name: str = 'dips', collection_name: str = 'events', indexes: dict = None):
        self.client = client or mongo_instance()
        self.db_name = db_name
        self.db = self.client[db_name]
        if db_name not in self.client.list_database_names():
            # Create a database with 400 RU throughput that can be shared across
            # the DB's collections
            self.db.command({"customAction": "CreateDatabase",
                             "offerThroughput": 400})
            print("Created db '{}' with shared throughput.\n".format(db_name))
        else:
            print("Using database: '{}'.\n".format(db_name))

        self.collection_name = collection_name
        self.collection = self.db[collection_name]

        if collection_name not in self.db.list_collection_names():
            # Creates a unsharded collection that uses the DBs shared throughput
            self.db.command(
                {"customAction": "CreateCollection", "collection": collection_name}
            )
            print("Created collection '{}'.\n".format(collection_name))
        else:
            print("Using collection: '{}'.\n".format(collection_name))

        self.indexes = indexes

        if self.indexes:
            self.db.command(
                {
                    "customAction": "UpdateCollection",
                    "collection": collection_name,
                    "indexes": indexes,
                }
            )

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
        self.mongo_service = MongoDBService()

    def get_next_id(self):
        counter = self.mongo_service.collection.find_one_and_update(
            {'_id': 'event_id'},
            {'$inc': {'seq': 1}},
            upsert=True,
            return_document=True
        )
        return counter['seq']

    def event(self, level: str, pid: str, message: str, status: str) -> None:
        """
        This method is used to log the status of a workflow
        """
        evt = {
            'level': level,
            'pid': pid,
            'message': message,
            'status': status,
            'ts': datetime.now(timezone.utc).isoformat(),
        }
        # Get the next auto-incremented ID
        evt['_id'] = self.get_next_id()
        self.mongo_service.upsert(evt['_id'], evt)
