from dataclasses import dataclass
import logging
import os

import psycopg2


@dataclass
class BlobInfo:
    id: str
    type: str
    blobName: str
    blobURI: str
    status: str
    ts: str

    @staticmethod
    def from_json(json_data: dict):
        return BlobInfo(
            id=json_data['id'],
            type=json_data['type'],
            blobName=json_data['blobName'],
            blobURI=json_data['blobURI'],
            status=json_data['status'],
            ts=json_data['ts']
        )

    def to_json(self):
        return {
            'id': self.id,
            'type': self.type,
            'blobName': self.blobName,
            'blobURI': self.blobURI,
            'status': self.status,
            'ts': self.ts
        }


def db_insert(blob_infor: BlobInfo):
    conn = psycopg2.connect(user=os.getenv('DB_USER'),
                            password=os.getenv('DB_PASSWORD'),
                            host=os.getenv('DB_HOST'),
                            port=os.getenv('DB_PORT'),
                            database=os.getenv('DB_DATABASE'))
    cursor = conn.cursor()

    # Create a table
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS events (id uuid PRIMARY KEY, type varchar(50), blobname varchar(100), bloburi varchar(100), status varchar(20), ts TIMESTAMP);")

    # Insert some data into the table
    try:
        cursor.execute(
            "INSERT INTO events (id,type,blobname,bloburi,status,ts) values (%s,%s,%s,%s,%s,%s);",
            (blob_infor.id, blob_infor.type, blob_infor.blobName, blob_infor.blobURI, blob_infor.status, blob_infor.ts))
    except Exception as e:
        logging.error(f'Error inserting data into the table: {e}')

    # Clean up

    conn.commit()
    cursor.close()
    conn.close()
