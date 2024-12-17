import logging
import os
from dotenv import load_dotenv


class Settings:
    def __init__(self):
        load_dotenv()
        # self.table_connection_string = os.getenv("TABLE_CONNECTION_STRING")
        # self.queue_connection_string = os.getenv("QUEUE_CONNECTION_STRING")
        self.blob_connection_string = os.getenv("STORAGE_CONNECTION_STRING")
        #print(self.blob_connection_string)
        # self.type = os.getenv("TYPE") or "azure"
        # self.chat_model = os.getenv("CHAT_MODEL")
        # self.endpoint = os.getenv("ENDPOINT")
        # self.api_key = os.getenv("API_KEY")
        # self.version = os.getenv("VERSION") or "2024-02-15-preview"
        # self.speech_region = os.getenv("SPEECH_REGION")
        # self.speech_key = os.getenv("SPEECH_API_KEY")
        # self.pg_host = os.getenv("PG_HOST")
        # self.pg_port = os.getenv("PG_PORT") or "5432"
        # self.pg_user = os.getenv("PG_USER") or "dbadmin"
        # self.pg_password = os.getenv("PG_PASSWORD")
        # self.pg_database = os.getenv("PG_DATABASE")
        # self.pg_sslmode = os.getenv("PG_SSLMODE")
        #self.mongo_conn_str = os.getenv("MONGO_DB")
        self.mongo_listconnectionstringurl = os.getenv("AZURE_COSMOS_LISTCONNECTIONSTRINGURL") # Azure CosmosDB list connection string URL Ex: 'https://management.azure.com/subscriptions/<subscription-ID>/resourceGroups/<resource-group-name>/providers/Microsoft.DocumentDB/databaseAccounts/<Azure-Cosmos-DB-API-for-MongoDB-account>/listConnectionStrings?api-version=2024-08-15'
        # self.storage_url = os.getenv("STORAGE_URL")
        # self.storage_key = os.getenv("STORAGE_KEY")

        # print(f"Settings: {self.__dict__}")

        # if not bool(self.table_connection_string) or not bool(self.queue_connection_string) \
        #         or not bool(self.blob_connection_string) or not bool(self.type) or not bool(self.chat_model) \
        #         or not bool(self.endpoint) or not bool(self.api_key) or not bool(self.version) \
        #         or not bool(self.speech_region) or not bool(self.speech_key) \
        #         or not bool(self.mongo_conn_str) or not bool(self.storage_url) \
        #         or not bool(self.storage_key):

        if not bool(self.blob_connection_string) or not bool(self.mongo_listconnectionstringurl):
            # os exist
            logging.error("Some or all missing environment variables STORAGE_CONNECTION_STRING, AZURE_COSMOS_LISTCONNECTIONSTRINGURL")
            exit(1)


settings = None


def get_settings_instance():
    global settings
    if settings is None:
        settings = Settings()
    return settings
