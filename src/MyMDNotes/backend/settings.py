import logging
import os
from dotenv import load_dotenv


class Settings:
    def __init__(self):
        load_dotenv()
        self._env = os.getenv("ENV")

        # Region: Azure Storage
        # Azure storage account URL
        self._storage_url = os.getenv("STORAGE_URL")
        # self.storage_key = os.getenv("STORAGE_KEY") # Azure storage account key
        # NOTE: Azure storage connection not used in PROD
        self._storage_connection_string = os.getenv("STORAGE_CONNECTION_STRING")
        # endregion: Azure Storage

        # Region: Mongo
        # Azure CosmosDB list connection string URL Ex: 'https://management.azure.com/subscriptions/<subscription-ID>/resourceGroups/<resource-group-name>/providers/Microsoft.DocumentDB/databaseAccounts/<Azure-Cosmos-DB-API-for-MongoDB-account>/listConnectionStrings?api-version=2024-08-15'
        self._mongo_listconnectionstringurl = os.getenv("AZURE_COSMOS_LISTCONNECTIONSTRINGURL")
        # NOTE: Mongo connection string not used in PROD
        self._mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
        # endregion: Mongo

        if not bool(self.blob_connection_string) or not bool(self.mongo_listconnectionstringurl):
            # os exist
            logging.error("Some or all missing environment variables STORAGE_CONNECTION_STRING, AZURE_COSMOS_LISTCONNECTIONSTRINGURL")
            exit(1)

    @property
    def is_dev(self) -> bool:
        if self._env is not None and (self._env.lower() == "dev" or self._env.lower() == "development"):
            return True
        return False

    @property
    def storage_connection_string(self) -> str:
        return self._storage_connection_string

    @property
    def storage_url(self) -> str:
        return self._storage_url

    @property
    def mongo_connection_string(self) -> str:
        return self._mongo_connection_string

    @property
    def mongo_listconnectionstringurl(self) -> str:
        return self._mongo_listconnectionstringurl


settings = None


def get_settings_instance():
    global settings
    if settings is None:
        settings = Settings()
    return settings
