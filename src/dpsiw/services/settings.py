import logging
import os
from dotenv import load_dotenv


class Settings:
    def __init__(self):
        load_dotenv()
        self.type = os.getenv("TYPE") or "azure" # OpenAI or Azure OpenAI
        self.chat_model = os.getenv("CHAT_MODEL") # gpt-4o
        self.endpoint = os.getenv("ENDPOINT") # Azure OpenAI endpoint or OpenAI endpoint
        #self.api_key = os.getenv("API_KEY") # Azure OpenAI key or OpenAI key
        self.version = os.getenv("VERSION") or "2024-02-15-preview" # API Azure OpenAI version
        self.speech_region = os.getenv("SPEECH_REGION") # Azure speech region
        self.azSpeechResourceId = os.getenv("SPEECH_RESOURCE_ID") # Azure speech resource ID
        #self.speech_key = os.getenv("SPEECH_API_KEY") # Azure speech key
        #self.mongo_conn_str = os.getenv("MONGO_DB") # CosmosDB MongoDB connection string
        self.mongo_listconnectionstringurl = os.getenv("AZURE_COSMOS_LISTCONNECTIONSTRINGURL") # Azure CosmosDB list connection string URL Ex: 'https://management.azure.com/subscriptions/<subscription-ID>/resourceGroups/<resource-group-name>/providers/Microsoft.DocumentDB/databaseAccounts/<Azure-Cosmos-DB-API-for-MongoDB-account>/listConnectionStrings?api-version=2024-08-15'
        self.storage_url = os.getenv("STORAGE_URL") # Azure storage account URL
        #self.storage_key = os.getenv("STORAGE_KEY") # Azure storage account key
        self.sb_connection_string = os.getenv("SB_CONNECTION_STRING") # Azure service bus connection string Ex: "<SB name>.servicebus.windows.net"
        self.sb_queue_name = os.getenv("SB_QUEUE") or "dips-messages" # Azure service bus queue name

        # if not bool(self.type) or not bool(self.chat_model) \
        #         or not bool(self.endpoint) or not bool(self.api_key) or not bool(self.version) \
        #         or not bool(self.speech_region) or not bool(self.speech_key) \
        #         or not bool(self.mongo_conn_str) or not bool(self.storage_url) \
        #         or not bool(self.storage_key) or not bool(self.sb_connection_string) \
        #         or not bool(self.sb_queue_name):

        if not bool(self.type) or not bool(self.chat_model) \
                or not bool(self.endpoint) or not bool(self.version) \
                or not bool(self.speech_region) or not bool(self.azSpeechResourceId) \
                or not bool(self.storage_url) \
                or not bool(self.sb_connection_string) \
                or not bool(self.sb_queue_name):
            # os exist
            # logging.error("Missing environment variables including TYPE, CHAT_MODEL, ENDPOINT, API_KEY, VERSION, SPEECH_REGION, " +
            #               "SPEECH_API_KEY, MONGO_DB, STORAGE_URL, STORAGE_KEY, SB_CONNECTION_STRING, SB_QUEUE")
            logging.error("Missing environment variables including TYPE, CHAT_MODEL, ENDPOINT, VERSION, SPEECH_REGION, SPEECH_RESOURCE_ID, " +
                          "MONGO_DB, STORAGE_URL, SB_CONNECTION_STRING, SB_QUEUE")
            exit(1)


settings = None


def get_settings_instance():
    global settings
    if settings is None:
        settings = Settings()
    return settings
