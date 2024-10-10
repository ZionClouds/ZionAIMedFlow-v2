from datetime import datetime
import json
import uuid
from .azuretable import TableManager


class EventSource:
    def __init__(self) -> None:
        client = TableManager.get_client()
        self.table_manager: TableManager = TableManager(client, 'dpsiw_events')

    def raise_event(self, event_type: str, event_data: dict):
        if not self.table_manager:
            raise Exception("Table manager not initialized")

        entity = {
            'PartitionKey': event_type,
            'RowKey': str(uuid.uuid4()),
            'data': json.dumps(event_data)
        }
        self.table_manager.upsert_entity(entity)

    def log_event(self, level: str = "INFO" | "WARN" | "DEBUG" | "ERROR" | "CRITICAL", message: str | None = None, id: str | None = None, correlation_id: str | None = None):
        if not self.table_manager:
            raise Exception("Table manager not initialized")

        entity = {
            'PartitionKey': level,
            'RowKey': str(uuid.uuid4()),
            'id': id,
            'correlationID': correlation_id,
            'message': message,
            'ts': str(datetime.datetime.now())
        }

        self.table_manager.upsert_entity(entity)
