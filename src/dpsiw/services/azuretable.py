from datetime import datetime
import logging
from azure.data.tables import TableServiceClient
from pydantic import BaseModel
from abc import ABC, abstractmethod


class Profile(BaseModel):
    specialty: str
    template: str


class Entity(BaseModel):
    partition_key: str = 'physician'
    row_key: str  # physician_id
    timestamp: datetime
    data: dict


class Database(ABC):
    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string
        self.connection = None

    @abstractmethod
    def insert(self, entity: Entity) -> None:
        pass

    def query(self, partition_key: str, row_key: str) -> Entity:
        pass

    @abstractmethod
    def query_all(self) -> list[Entity]:
        pass

    @abstractmethod
    def query_by_partition_key(self, partition_key: str) -> list[Entity]:
        pass

    @abstractmethod
    def delete(self, partition_key: str, row_key: str) -> None:
        pass

    @abstractmethod
    def delete_all(self) -> None:
        pass


class TableManager:
    """
    Azure Table Service Manager
    """

    def __init__(self, client: TableServiceClient, table_name: str = "DPSIw") -> None:
        self.client = client
        self.table_name = table_name
        self.table_found = False
        try:
            self.client.create_table_if_not_exists(self.table_name)
        except Exception as e:
            logging.error(f"Table creation failed: {e}")

    # TODO: Remove connection_string and use environment variables
    @staticmethod
    def get_client(connection_string: str) -> TableServiceClient:
        return TableServiceClient.from_connection_string(
            conn_str=connection_string)

    def table_exists(self) -> bool:
        tables = self.client.list_tables()
        print(tables)
        return self.table_name in tables

    def create_table(self) -> None:
        if not self.table_exists():
            try:
                self.client.create_table(self.table_name)
            except Exception as e:
                logging.error(f"Table creation failed: {e}")

    def create_entity(self, entity: dict) -> None:
        table_client = self.client.get_table_client(table_name=self.table_name)
        table_client.create_entity(entity=entity)

    def upsert_entity(self, entity: dict) -> None:
        # self.create_table()
        table_client = self.client.get_table_client(table_name=self.table_name)
        table_client.upsert_entity(entity=entity)

    def upsert_entities_batch(self, entities: list) -> None:
        table_client = self.client.get_table_client(table_name=self.table_name)
        for entity in entities:
            table_client.upsert_entity(entity=entity)

    def get_by_partition_key(self, partition_key: str, row_key: str, **kwargs: any) -> list:
        table_client = self.client.get_table_client(table_name=self.table_name)
        entity = table_client.get_entity(
            partition_key=partition_key, row_key=row_key, **kwargs)
        return entity

    def get_all_entities(self) -> list:
        try:
            table_client = self.client.get_table_client(
                table_name=self.table_name)
            entities = table_client.list_entities()
        except Exception as e:
            entities = []
            # logging.error(f"Error getting entities: {e}")
        return entities

    def query_table(self, filter: str) -> list:
        # my_filter = "PartitionKey eq 'RedMarker'"
        table_client = self.client.get_table_client(table_name=self.table_name)
        entities = table_client.query_entities(query_filter=filter)
        return entities

    def delete_table(self) -> None:
        table_client = self.client.get_table_client(table_name=self.table_name)
        table_client.delete_table()

    def delete_all_entities(self) -> None:
        table_client = self.client.get_table_client(table_name=self.table_name)
        entities = table_client.query_entities(query_filter='1 eq 1')
        for entity in entities:
            table_client.delete_entity(
                partition_key=entity['PartitionKey'], row_key=entity['RowKey'])

    def delete_entity(self, partition_key: str, row_key: str) -> None:
        table_client = self.client.get_table_client(table_name=self.table_name)
        table_client.delete_entity(
            partition_key=partition_key, row_key=row_key)
