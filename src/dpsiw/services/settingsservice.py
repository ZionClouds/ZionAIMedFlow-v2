import logging
import os
from dotenv import load_dotenv


class SettingsService:
    """
    Settings class to load environment variables to support local development with keys and with managed identity in Azure
    """

    def __init__(self):
        load_dotenv()
        self._env = os.getenv("ENV")

        # Region: OpenAI
        self._type = os.getenv("TYPE") or "azure"  # OpenAI or Azure OpenAI
        self._chat_model = os.getenv("CHAT_MODEL") or "gpt-4o"  # gpt-4o
        # Azure OpenAI endpoint or OpenAI endpoint
        self._openai_endpoint = os.getenv("OPENAI_ENDPOINT")
        # API Azure OpenAI version
        self._openai_version = os.getenv(
            "OPENAI_VERSION") or "2024-02-15-preview"
        # NOTE: Azure OpenAI key or OpenAI key not used in PROD
        # Azure OpenAI key or OpenAI key
        self._openai_key = os.getenv("OPENAI_KEY")
        # endregion: OpenAI

        # Region: Speech
        self._speech_region = os.getenv("SPEECH_REGION")  # Azure speech region
        self._azSpeechResourceId = os.getenv(
            "SPEECH_RESOURCE_ID")  # Azure speech resource ID
        # NOTE: Azure speech key not used in PROD
        self._speech_key = os.getenv("SPEECH_KEY")  # Azure speech key
        # endregion: Speech

        # Region: Mongo
        # Azure CosmosDB list connection string URL Ex: 'https://management.azure.com/subscriptions/<subscription-ID>/resourceGroups/<resource-group-name>/providers/Microsoft.DocumentDB/databaseAccounts/<Azure-Cosmos-DB-API-for-MongoDB-account>/listConnectionStrings?api-version=2024-08-15'
        self._mongo_listconnectionstringurl = os.getenv(
            "AZURE_COSMOS_LISTCONNECTIONSTRINGURL")
        # NOTE: Mongo connection string not used in PROD
        self._mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
        # endregion: Mongo

        # Region: Azure Storage
        # Azure storage account URL
        self._storage_url = os.getenv("STORAGE_URL")
        # self.storage_key = os.getenv("STORAGE_KEY") # Azure storage account key
        # NOTE: Azure storage connection not used in PROD
        self._storage_connection_string = os.getenv(
            "STORAGE_CONNECTION_STRING")
        # endregion: Azure Storage

        # Region: Azure Service Bus
        # Azure service bus namespace
        self._sb_mi_ns = os.getenv("SB_MI_NS")
        # Azure service bus worker queue name
        self._sb_queue_name = os.getenv("SB_QUEUE") or "dips-messages"
        # NOTE: Storage connection string not used in PROD
        self._sb_connection_string = os.getenv("SB_CONNECTION_STRING")
        # endregion: Azure Service Bus

        if self.is_dev:
            if not bool(self._type) or not bool(self._chat_model) \
                    or not bool(self._openai_endpoint) or not bool(self._openai_version) or not bool(self._openai_key) \
                    or not bool(self._speech_region) or not bool(self._speech_key) \
                    or not bool(self._storage_connection_string) \
                    or not bool(self._mongo_connection_string) \
                    or not bool(self.sb_connection_string) \
                    or not bool(self._sb_queue_name):
                # os exist
                # logging.error("Missing environment variables including TYPE, CHAT_MODEL, ENDPOINT, API_KEY, VERSION, SPEECH_REGION, " +
                #               "SPEECH_API_KEY, MONGO_DB, STORAGE_URL, STORAGE_KEY, SB_CONNECTION_STRING, SB_QUEUE")
                logging.error("Missing DEV environment variables including TYPE, CHAT_MODEL, ENDPOINT, API_KEY, VERSION, SPEECH_REGION, " +
                              "SPEECH_API_KEY, MONGO_CONNECTION_STRING, STORAGE_CONNECTION_STRING, SB_CONNECTION_STRING, SB_QUEUE")

                exit(1)
        else:
            if not bool(self._type) or not bool(self._chat_model) \
                    or not bool(self._openai_endpoint) or not bool(self._openai_version) \
                    or not bool(self._speech_region) or not bool(self._azSpeechResourceId) \
                    or not bool(self._storage_url) \
                    or not bool(self._sb_mi_ns) \
                    or not bool(self._sb_queue_name):
                # os exist
                # logging.error("Missing environment variables including TYPE, CHAT_MODEL, ENDPOINT, API_KEY, VERSION, SPEECH_REGION, " +
                #               "SPEECH_API_KEY, MONGO_DB, STORAGE_URL, STORAGE_KEY, SB_CONNECTION_STRING, SB_QUEUE")
                logging.error("Missing PROD environment variables including TYPE, CHAT_MODEL, ENDPOINT, VERSION, SPEECH_REGION, SPEECH_RESOURCE_ID, " +
                              "MONGO_DB, STORAGE_URL, SB_CONNECTION_STRING, SB_QUEUE")
                exit(1)

    @property
    def is_dev(self) -> bool:
        if self._env is not None and (self._env.lower() == "dev" or self._env.lower() == "development"):
            return True
        return False

    @property
    def type(self) -> str:
        return self._type

    @property
    def chat_model(self) -> str:
        return self._chat_model

    @property
    def openai_endpoint(self) -> str:
        return self._openai_endpoint

    @property
    def openai_key(self) -> str:
        return self._openai_key

    @property
    def openai_version(self):
        return self._openai_version

    @property
    def speech_region(self) -> str:
        return self._speech_region

    @property
    def speech_key(self) -> str:
        return self._speech_key

    @property
    def azSpeechResourceId(self) -> str:
        return self._azSpeechResourceId

    @property
    def mongo_connection_string(self) -> str:
        return self._mongo_connection_string

    @property
    def mongo_listconnectionstringurl(self) -> str:
        return self._mongo_listconnectionstringurl

    @property
    def storage_connection_string(self) -> str:
        return self._storage_connection_string

    @property
    def storage_url(self) -> str:
        return self._storage_url

    @property
    def storage_key(self) -> str:
        return self._storage_key

    @property
    def sb_queue_name(self) -> str:
        return self._sb_queue_name

    @property
    def sb_connection_string(self) -> str:
        return self._sb_connection_string

    @property
    def sb_mi_ns(self) -> str:
        return self._sb_mi_ns


settings = None


def get_settings_instance():
    global settings
    if settings is None:
        settings = SettingsService()
    return settings
